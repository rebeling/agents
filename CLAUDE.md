# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Development commands (use uv for package management)
uv run python export_dialogues.py          # Export Redis chats to markdown
uv run python app/dynamic_agent_starter.py # Start all active agents
uv run python app/chat_server.py           # Start main chat interface on port 7999

# Code quality
uv run task format     # Format code with ruff
uv run task check      # Lint and fix with ruff
uv run task test       # Run pytest tests

# Manual agent management
bash scripts/run-agents.sh                 # Alternative agent startup script
```

## Architecture Overview

### Multi-Agent Chat System
This is a Redis pub/sub based multi-agent conversation system using pydantic-ai. The system enables real-time conversations between AI personalities and users through a web interface.

### Core Components

**Agent Registry (`app/agents.yml`)**
- Defines agent personalities (Dominique, Joseph, Giulio, Ada, Crispin)
- Each agent has `active` flag, `name`, and `system_prompt`
- Meta section contains shared prompt patterns and token limits
- Only agents marked `active: true` are started

**Agent Architecture**
- `FastAgent` class (`app/agents/agent.py`) wraps pydantic-ai agents with FastAPI
- Each agent runs on separate port (8001+) and listens to shared Redis channel
- Agents respond only when message sender != their own name
- Message history stored in Redis lists as ModelMessages JSON

**Communication Flow**
```
User → WebSocket (port 7999) → Redis pub/sub → Active Agents → LLM → Redis → WebSocket → User
```

**Model Configuration (`app/core/provider.py`)**
- Supports Anthropic Claude (current), OpenRouter API, and local Ollama
- Model settings include token limits (currently 100 max tokens)
- Channel names auto-generated: `chat-{date}-{sanitized-model-name}`

**Data Storage**
- Real-time messages: Redis pub/sub channels
- History: Redis lists (`{channel}_history`) containing pydantic-ai ModelMessages
- Export: `app/core/redis_export.py` provides functions to list topics, get messages, export to markdown

### Key Files
- `app/core/redis.py` - Redis configuration, connection, and core handler
- `app/core/redis_export.py` - Chat export utilities (separated from core Redis)
- `app/chat_server.py` - Main web interface with WebSocket
- `app/core/registry.py` - Agent registry loading and process management
- `app/core/utils.py` - Shared utilities (YAML loading, prompt combination)
- `app/dynamic_agent_starter.py` - Multi-process agent launcher
- `export_dialogues.py` - Batch export all chats to `agent-dialogues/` folder

### Environment Requirements
- Redis server running on localhost:6379
- `ANTHROPIC_API_KEY` environment variable for Claude access (current default)
- `OPENROUTER_API_KEY` environment variable for OpenRouter LLM access (optional)
- Python 3.11+ with uv package manager

### Recent Simplifications
- Consolidated `app/helpers/` directory into `app/core/redis_export.py` 
- Removed duplicate utility functions between `registry.py` and `utils.py`
- Split Redis functionality: core operations in `redis.py`, export utilities in `redis_export.py`
- Reduced codebase from 1,200+ lines to ~800 lines while maintaining all functionality