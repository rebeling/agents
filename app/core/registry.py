"""Agent registry loading and management."""

import multiprocessing
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI

from app.core.provider import MAX_RESPONSE_TOKENS

today = datetime.now().strftime("%B %d, %Y")


def load_agent_registry() -> dict:
    """Load the agent registry YAML file."""
    registry_path = Path(__file__).parent.parent / "agents.yml"
    with open(registry_path) as f:
        return yaml.safe_load(f)


def get_active_agents(registry: dict) -> list[dict]:
    """Extract list of active agents with their configurations."""
    active_agents = []
    if "agents" in registry:
        for agent_name, agent_config in registry["agents"].items():
            if agent_config.get("active", False):
                combined_prompt = combine_prompt(registry["meta"], agent_config)
                agent_data = {
                    "name": agent_config.get("name", agent_name.title()),
                    "system_prompt": combined_prompt,
                }
                active_agents.append(agent_data)
    return active_agents


def combine_prompt(registry_meta, agent_config):
    """
    Combine registry meta information with agent configuration to create a complete prompt.

    Args:
        registry_meta: Meta configuration from agent registry (contains prompt and patterns)
        agent_config: Individual agent configuration (contains system_prompt, meta_prompt, patterns)

    Returns:
        str: Combined prompt string
    """
    the_prompt = []

    # Add the main system prompt
    system_prompt = agent_config["system_prompt"]
    the_prompt.append(system_prompt)

    # Add registry meta prompt and patterns
    if registry_meta:
        meta_prompt = registry_meta["prompt"].format(
            TODAY=today, MAX_RESPONSE_TOKENS=MAX_RESPONSE_TOKENS
        )
        the_prompt.append(meta_prompt)

    # Join all parts
    combined_prompt = "".join(the_prompt)
    print(combined_prompt)
    return combined_prompt


def create_agent_app(agent_config: dict) -> FastAPI:
    """Create a FastAPI app for a single agent."""
    try:
        from app.agents.agent import FastAgent

        fast_agent = FastAgent(a2a=agent_config)
        return fast_agent.app
    except Exception as e:
        print(f"Error creating agent {agent_config['name']}: {e}")
        # Fallback to simple FastAPI app
        app = FastAPI()

        @app.get("/")
        async def root():
            return {"message": f"Hello from {agent_config['name']}"}

        return app


def start_agent_process(agent_config: dict, port: int):
    """Start a single agent in its own process."""

    def signal_handler(_signum, _frame):
        print(f"\nShutting down {agent_config['name']} on port {port}...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting {agent_config['name']} on port {port}...")

    app = create_agent_app(agent_config)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


def start_rebel_agent():
    """Start the Agent Rebel (chat server) process."""

    def signal_handler(_signum, _frame):
        print("\nShutting down Agent Rebel on port 7999...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Starting Agent Rebel on port 7999...")

    uvicorn.run(
        "app.chat_server:app", host="0.0.0.0", port=7999, reload=False, log_level="info"
    )


def start_all_agents():
    """Start all active agents and the chat server."""
    processes = []

    try:
        # Load agent registry
        print("Loading agent registry...")
        registry = load_agent_registry()

        # Get active agents
        active_agents = get_active_agents(registry)
        print(f"Found {len(active_agents)} active agents")

        # Start Agent Rebel in separate process
        rebel_process = multiprocessing.Process(target=start_rebel_agent)
        rebel_process.start()
        processes.append(rebel_process)

        # Give Agent Rebel time to start
        time.sleep(3)

        # Start each active agent in its own process
        starting_port = 8001

        for i, agent_config in enumerate(active_agents):
            port = starting_port + i
            process = multiprocessing.Process(
                target=start_agent_process, args=(agent_config, port)
            )
            process.start()
            processes.append(process)

            print(f"Started {agent_config['name']} on port {port}")
            time.sleep(2)

        print(f"\nAll {len(active_agents)} agents started successfully!")
        print("Ports:")
        print("  - Agent Rebel: 7999")
        for i, agent_config in enumerate(active_agents):
            print(f"  - {agent_config['name']}: {starting_port + i}")

        print("\nPress Ctrl+C to stop all agents...")

        # Wait for all processes
        try:
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            print("\nStopping all agents...")

    except KeyboardInterrupt:
        print("\nStopping all agents...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()

        print("All agents stopped.")


__all__ = [
    "load_agent_registry",
    "get_active_agents",
    "start_all_agents",
    "start_agent_process",
]
