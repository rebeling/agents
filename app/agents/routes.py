"""API route handlers for FastAgent."""

from fastapi import FastAPI
from app.core.models import ChatRequest, ChatResponse
from app.agents.info import get_agent_info, create_agent_card


def add_agent_routes(
    app: FastAPI,
    agent_name: str,
    system_prompt: str,
    redis_channel: str,
    agent_run_func,
):
    """Add all agent API routes to FastAPI app."""

    @app.get("/")
    async def agent_info():
        return get_agent_info(agent_name, system_prompt, redis_channel)

    @app.post("/chat", response_model=ChatResponse)
    async def chat_with_agent(request: ChatRequest):
        try:
            response = await agent_run_func(request.message)
            return ChatResponse(response=response.output, agent_name=agent_name)
        except Exception as e:
            return ChatResponse(response=f"Error: {str(e)}", agent_name=agent_name)

    @app.get("/.well-known/agent.json")
    async def agent_manifest():
        return create_agent_card(agent_name, system_prompt)
