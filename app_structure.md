# Suggested App Folder Structure

```
app/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── agents.yml                  # Agent definitions and personalities
│   ├── provider.py                 # LLM model configuration
│   └── specs.py                    # Redis and system configuration
├── core/
│   ├── __init__.py
│   ├── agent_base.py              # FastAgent class - core agent logic
│   ├── models.py                   # Pydantic models for data structures
│   └── utils.py                    # Utility functions (combine_prompt, etc.)
├── services/
│   ├── __init__.py
│   ├── dialogues.py               # Chat export and management utilities
│   └── redis_service.py           # Redis operations (optional refactor)
├── web/
│   ├── __init__.py
│   ├── agent_0.py                 # Main web interface with WebSocket
│   ├── frontend/
│   │   ├── static/
│   │   │   └── style.css
│   │   └── templates/
│   │       └── index.html
├── scripts/
│   ├── __init__.py
│   ├── dynamic_agent_starter.py   # Multi-agent startup script
│   ├── export_dialogues.py        # Export all chats to markdown
│   ├── inspect_redis.py           # Debug Redis data structures
│   └── find_message.py            # Search specific messages
└── agents/
    ├── __init__.py
    └── personalities/              # Individual agent files (if needed)
```

## Benefits of This Structure

1. **Separation of Concerns**:
   - `config/` - All configuration and setup
   - `core/` - Core business logic and agent framework
   - `services/` - Data access and external service integrations
   - `web/` - Web interface and frontend assets
   - `scripts/` - Utility scripts and tools

2. **Scalability**: Easy to add new services, agents, or web endpoints

3. **Maintainability**: Clear boundaries between different system components

4. **Testing**: Each module can be tested independently

## Migration Commands

```bash
# Create new structure
mkdir -p app/{config,core,services,web,agents/personalities}

# Move existing files
mv app/agent_registry.yml app/config/
mv app/provider.py app/config/
mv app/specs.py app/config/
mv app/agent_base.py app/core/
mv app/models.py app/core/
mv app/utils.py app/core/
mv app/dialogues.py app/services/
mv app/agent_0.py app/web/
mv app/dynamic_agent_starter.py app/scripts/
```