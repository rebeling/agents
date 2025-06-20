# Agents

A multi-agent conversational AI system where independent AI personalities communicate through Redis pub/sub channels in real-time. Each agent runs as a separate process with its own FastAPI endpoint, enabling scalable and distributed AI conversations. The system supports various LLM providers and provides a web interface for a human in the loop.

## Architecture

The system consists of independent agent processes that communicate via Redis pub/sub:

- **Agent Registry**: YAML configuration defining agent personalities and system prompts
- **Agent Processes**: Each agent runs independently on separate ports (8001+) with FastAPI endpoints
- **Redis Communication**: Pub/sub channels enable real-time message exchange between agents
- **Web Interface**: Chat server on port 7999 provides WebSocket interface for human interaction
- **Message History**: Persistent storage of conversations using Redis lists with pydantic-ai ModelMessages
- **Export System**: Tools to export conversations to markdown format for analysis

## Todos:
* [ ] dialog to audio with different voices - tts elevenlabs
* [ ] add tools to the agents, string in config and refernce to code
* [ ] tool1 an agent with a tool to create diacritics or audio streams
* [ ] tool2 an agent is able to pull the dialogs from redis


## Project Progress

Initial idea: they work together as a team on a task and communicate in human language. Less human interaction, more complex workflows, based on the idea llm-as-a-judge they control, organize themselves with each other. Not only different tools, so specialzed in certain tasks, but also great work based on personalities: the planer, the thinker, the coordinator, ...

* started with to much personality description, dialogs were: super chatty fleurish from simple: lets do it, ok, now, begin, yes, ok, lets begin,...to super hearty flirty interactions between the agents - with most expensive anthropic model they flirted 10m for around 10$, not knowing that they are llm agents.
* or the dialogs where just broken, on syntax, repetiions, circles, loops, not even heading against a goal
* and they did not followed instructions from agent rebel or just ignored me ...even when started one agent for testing it called for the other agent from message history
* based on the claude prompt leak defined some does and donts and create meta prompt
* started of with super descriptive prompts on human conversations, and defined rules and boundaries and it gets better



## The providers

* Local ollama https://ollama.ai/
* Openrouter multiple LLMs https://openrouter.ai/
* Anthropic Claude Pricing https://docs.anthropic.com/en/docs/about-claude/pricing
