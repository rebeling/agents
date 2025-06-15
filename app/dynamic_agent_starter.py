#!/usr/bin/env python3
"""
Dynamic agent starter that reads from agent_registry.yml and creates
FastAPI apps for each active agent, starting uvicorn on sequential ports.
"""

import multiprocessing

from app.core.registry import start_all_agents


def main():
    """Main function to start all active agents."""
    start_all_agents()


if __name__ == "__main__":
    # Required for multiprocessing on some systems
    multiprocessing.set_start_method("spawn", force=True)
    main()
