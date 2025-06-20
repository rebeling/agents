"""Redis export utilities for chat dialogues."""

from datetime import datetime
from pydantic_ai.messages import ModelMessagesTypeAdapter
from app.core.redis import redis_client


async def list_chat_topics() -> list[str]:
    """List all chat topics (channels) stored in Redis."""
    try:
        chat_keys = await redis_client.keys("*-chat-*")
        history_keys = await redis_client.keys("*-chat-*_history")
        
        topics = set()
        for key in chat_keys:
            if not key.endswith("_history"):
                topics.add(key)
        
        for key in history_keys:
            base_key = key.replace("_history", "")
            topics.add(base_key)
            
        return sorted(topics)
    except Exception as e:
        print(f"Error listing chat topics: {e}")
        return []


async def get_chat_messages(topic: str, limit: int = 50) -> list[dict]:
    """Get chat messages for a specific topic from Redis."""
    try:
        messages = []
        history_key = f"{topic}_history"
        raw_history = await redis_client.lrange(history_key, -limit, -1)
        
        for item in raw_history:
            try:
                json_data = item.decode("utf-8") if isinstance(item, bytes) else item
                parsed_messages = ModelMessagesTypeAdapter.validate_json(json_data)
                
                for msg in parsed_messages:
                    if hasattr(msg, "parts") and msg.parts:
                        for part in msg.parts:
                            if hasattr(part, "content"):
                                content = part.content
                                timestamp = datetime.now().isoformat()
                                messages.append({
                                    "content": content,
                                    "timestamp": timestamp,
                                    "role": getattr(msg, "kind", "unknown")
                                })
            except Exception as e:
                print(f"Error parsing message: {e}")
                
        return messages
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return []


async def export_topic_to_markdown(topic: str) -> str:
    """Export a topic's messages to markdown format."""
    messages = await get_chat_messages(topic)
    
    markdown_lines = [f"# Chat Export: {topic}\n"]
    markdown_lines.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for msg in messages:
        timestamp = msg.get("timestamp", "")
        content = msg.get("content", "")
        role = msg.get("role", "")
        
        markdown_lines.append(f"**{role}** ({timestamp})")
        markdown_lines.append(f"{content}\n")
        
    return "\n".join(markdown_lines)