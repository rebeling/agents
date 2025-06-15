"""Agent information gathering utilities using pydantic-ai FastA2A standards."""

from fasta2a.schema import AgentCard, Capabilities, Authentication
from app.core.provider import agent_model, model_settings


def get_model_info() -> dict:
    """Get comprehensive model information."""
    return {
        "model_name": str(agent_model.model_name),
        "base_url": str(agent_model.base_url),
        "provider": _detect_provider(agent_model.base_url),
        "settings": model_settings,
    }


def create_agent_card(agent_name: str, system_prompt: str) -> AgentCard:
    """Create a proper AgentCard following FastA2A standards."""
    return AgentCard(
        name=agent_name,
        description=system_prompt[:200] + "..."
        if len(system_prompt) > 200
        else system_prompt,
        version="1.0.0",
        default_input_modes=["application/json", "text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=Capabilities(
            streaming=False,
            push_notifications=True,  # We support Redis pub/sub
        ),
        authentication=Authentication(schemes=[]),
    )


def get_agent_info(agent_name: str, system_prompt: str, redis_channel: str) -> dict:
    """Get comprehensive agent information with FastA2A compatibility."""
    agent_card = create_agent_card(agent_name, system_prompt)

    return {
        "agent_card": agent_card,
        "system_prompt": system_prompt,
        "model_info": get_model_info(),
        "redis_config": {
            "channel": redis_channel,
            "history_key": f"{redis_channel}_history",
        },
        "endpoints": {
            "chat": "POST /chat - Direct agent interaction",
            "agent_card": "GET /.well-known/agent.json - FastA2A agent card",
            "docs": "GET /docs - API documentation",
        },
    }


def get_a2a_params(agent_name: str, system_prompt: str) -> dict:
    """Get parameters for agent.to_a2a() method."""
    return {
        "name": agent_name,
        "description": system_prompt[:200] + "..."
        if len(system_prompt) > 200
        else system_prompt,
        "version": "1.0.0",
    }


def _detect_provider(base_url: str) -> str:
    """Detect provider from base URL."""
    base_url_str = str(base_url).lower()
    if "openrouter" in base_url_str:
        return "OpenRouter"
    elif "localhost" in base_url_str:
        return "Local"
    else:
        return "Unknown"
