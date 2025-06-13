import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

from app.specs import REDIS_CHANNEL, agent_model, model_settings, redis_client


class FastAgent:
    def __init__(self, a2a: dict, redis_channel: str = REDIS_CHANNEL):
        self.name = a2a["name"]
        self.system_prompt = a2a["system_prompt"]
        self.redis_channel = redis_channel
        self.redis_history = f"{self.redis_channel}_history"

        self.agent = Agent(
            model=agent_model,
            system_prompt=self.system_prompt,
            model_settings=model_settings,
        )
        self.app = FastAPI(lifespan=self._lifespan)

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        print(f"Starting up FastAgent '{self.name}'...")
        asyncio.create_task(self._message_handler())
        yield
        print(f"Shutting down FastAgent '{self.name}'...")

    async def _message_handler(self):
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(self.redis_channel)

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                # print(f"Received message: {type(message)}")
                try:
                    chat_message = json.loads(message["data"])
                    _msg_to_process = ""
                    sender = chat_message["sender"]
                    if "content" in chat_message:
                        content = chat_message["content"]
                        _msg_to_process = f"{sender}: {content}"
                    else:
                        content = chat_message["response"]
                        _msg_to_process = f"{content}"

                    if sender != self.name:
                        response = await self._agent_call(_msg_to_process)
                        await self._publish(response)

                except Exception as e:
                    print(f"[{self.name}] Error handling message: {e}")
            await asyncio.sleep(0.01)

    async def _agent_call(self, message: str) -> str:
        try:
            messages = await self._message_history()
            response = await self.agent.run(message, message_history=messages)
            return response
        except Exception as e:
            print(f"[{self.name}] Agent failed: {e}")
            return f"**{self.name}:** Sorry, I couldn’t process that."

    async def _message_history(self) -> list[ModelMessage]:
        # Fetch the last N messages from Redis (change N as needed)
        raw = await redis_client.lrange(self.redis_history, -10, -1)
        messages: list[ModelMessage] = []
        for item in raw:
            try:
                # Redis returns bytes, decode to str
                json_data = item.decode("utf-8") if isinstance(item, bytes) else item
                # Validate and parse as list of ModelMessages
                parsed = ModelMessagesTypeAdapter.validate_json(json_data)
                messages.extend(parsed)
            except Exception as e:
                print(f"Invalid message format in Redis: {e}")
        return messages

    async def _publish(self, response):
        try:
            chat_message = {
                "type": "message",
                "content": f"{response.output.strip()}",
                "sender": self.name,
                "timestamp": datetime.now().isoformat(),
                "role": "user",
            }
            json_chat_message = json.dumps(chat_message)
            await redis_client.publish(self.redis_channel, json_chat_message)
            await redis_client.rpush(self.redis_history, response.new_messages_json())
        # restrict to -n last items ..
        # await redis_client.ltrim(f"{self.redis_history}", -10, -1)
        except Exception as e:
            print(f"{self.name} _publish {response} {e}")
