"""Redis configuration, connection, and handler utilities."""

import asyncio
import json
from datetime import datetime

import redis.asyncio as aioredis
from decouple import config
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

# Redis connection
redis_client = aioredis.from_url(
    config("REDIS_URL", default="redis://localhost:6379"),
    encoding="utf-8",
    decode_responses=True,
)

# Create unique channel name including model for multi-model support
today = datetime.now().strftime("%Y-%m-%d")
model_name_sanitized = (
    config("MODEL_NAME", default="unknown").replace("/", "-").replace(":", "-")
)

# import random
# ra = random.randint(1, 5000)

REDIS_CHANNEL = f"chat-{today}-{model_name_sanitized}"


class RedisHandler:
    """Handles Redis pub/sub operations for agents."""

    def __init__(self, agent_name: str, redis_channel: str, redis_history: str):
        self.agent_name = agent_name
        self.redis_channel = redis_channel
        self.redis_history = redis_history

    async def listen_and_respond(self, agent_call_func):
        """Listen for Redis messages and respond using agent_call_func."""
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(self.redis_channel)

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                try:
                    await self._process_message(message, agent_call_func)
                except Exception as e:
                    print(f"[{self.agent_name}] Error handling message: {e}")
            await asyncio.sleep(0.5)

    async def _process_message(self, message, agent_call_func):
        """Process a single Redis message."""
        chat_message = json.loads(message["data"])
        sender = chat_message["sender"]

        if sender == self.agent_name:
            return

        content = chat_message.get("content", chat_message.get("response", ""))
        msg_to_process = (
            f"{sender}: {content}" if "content" in chat_message else content
        )

        msg = msg_to_process[:60] + "..." if len(msg_to_process) > 60 else ""
        print(f"📥 [{self.agent_name}] Received from {sender}: {msg}")

        response = await agent_call_func(msg_to_process)
        await self.publish_response(response)

    async def publish_response(self, response):
        """Publish agent response to Redis."""
        try:
            chat_message = {
                "type": "message",
                "content": response.output.strip(),
                "sender": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "role": "user",
            }

            print(f"Publish to Redis by {self.agent_name}: {chat_message['content']}")
            if not chat_message["content"]:
                print(response)

            await redis_client.publish(self.redis_channel, json.dumps(chat_message))
            await self._store_message_history(response)

            # Add small pause after publishing response
            await asyncio.sleep(1)

        except Exception as e:
            print(f"{self.agent_name} publish error: {e}")

    async def _store_message_history(self, response):
        """Store message with sender metadata in Redis history."""
        messages_data = json.loads(response.new_messages_json())
        for msg in messages_data:
            if msg.get("kind") == "response":
                msg["agent_sender"] = self.agent_name

        enhanced_messages_json = json.dumps(messages_data)
        await redis_client.rpush(self.redis_history, enhanced_messages_json)

    async def get_message_history(self) -> list[ModelMessage]:
        """Fetch recent message history from Redis."""
        raw = await redis_client.lrange(self.redis_history, -10, -1)
        messages: list[ModelMessage] = []

        for item in raw:
            try:
                json_data = item.decode("utf-8") if isinstance(item, bytes) else item
                parsed = ModelMessagesTypeAdapter.validate_json(json_data)
                messages.extend(parsed)
            except Exception as e:
                print(f"Invalid message format in Redis: {e}")

        return messages


async def publish_to_redis(msg):
    """Publish a chat message to Redis channel."""
    try:
        await redis_client.publish(REDIS_CHANNEL, json.dumps(msg.model_dump()))
    except Exception as e:
        print(f"Error publishing to Redis: {e}")


__all__ = ["redis_client", "REDIS_CHANNEL", "RedisHandler", "publish_to_redis"]
