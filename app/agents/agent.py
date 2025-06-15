import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_ai import Agent

from app.core.provider import agent_model, model_settings
from app.core.redis import REDIS_CHANNEL, RedisHandler
from app.agents.info import get_a2a_params
from app.agents.routes import add_agent_routes


class FastAgent:
    def __init__(self, a2a: dict, redis_channel: str = REDIS_CHANNEL):
        self.name = a2a["name"]
        self.system_prompt = a2a["system_prompt"]
        self.redis_channel = redis_channel
        self.redis_history = f"{self.redis_channel}_history"

        self.agent = Agent(
            agent_model, system_prompt=self.system_prompt, model_settings=model_settings
        )
        self.redis_handler = RedisHandler(
            self.name, self.redis_channel, self.redis_history
        )
        self.app = FastAPI(lifespan=self._lifespan)

        add_agent_routes(
            self.app,
            self.name,
            self.system_prompt,
            self.redis_channel,
            self._agent_call,
        )

    def get_a2a_app(self):
        """Get a standalone FastA2A application for this agent."""
        return self.agent.to_a2a(**get_a2a_params(self.name, self.system_prompt))

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        print(f"Starting up FastAgent '{self.name}'...")
        asyncio.create_task(self.redis_handler.listen_and_respond(self._agent_call))
        yield
        print(f"Shutting down FastAgent '{self.name}'...")

    async def _agent_call(self, message: str):
        """Process message with agent and return response."""
        try:
            print(
                f"🤖 [{self.name}] Processing: {message[:100]}{'...' if len(message) > 100 else ''}"
            )
            messages = await self.redis_handler.get_message_history()
            response = await self.agent.run(message, message_history=messages)
            print(
                f"✅ [{self.name}] Response: {response.output[:100]}{'...' if len(response.output) > 100 else ''}"
            )
            return response
        except Exception as e:
            print(f"❌ [{self.name}] Agent failed: {e}")
            return f"**{self.name}:** Sorry, I couldn't process that."
