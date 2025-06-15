from datetime import datetime
from typing import Any

from pydantic_ai.messages import ModelMessagesTypeAdapter

from app.core.redis import redis_client


async def list_chat_topics() -> list[str]:
    """
    List all chat topics (channels) stored in Redis.
    Returns channel names that match the chat pattern.
    """
    try:
        # Get all keys that match the chat pattern
        chat_keys = await redis_client.keys("*-chat-*")

        # Also get history keys to find topics with stored messages
        history_keys = await redis_client.keys("*-chat-*_history")

        # Extract base topic names
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


async def get_chat_messages(topic: str, limit: int = 50) -> list[dict[str, Any]]:
    """
    Get chat messages for a specific topic from Redis.

    Args:
        topic: The chat topic/channel name
        limit: Maximum number of messages to retrieve (default 50)

    Returns:
        List of chat messages with metadata
    """
    try:
        messages = []
        history_key = f"{topic}_history"

        # Get stored message history (ModelMessages format)
        raw_history = await redis_client.lrange(history_key, -limit, -1)

        # Keep track of last seen agent name from system prompts across all entries
        current_agent = "Assistant"

        for item in raw_history:
            try:
                json_data = item.decode("utf-8") if isinstance(item, bytes) else item
                parsed_messages = ModelMessagesTypeAdapter.validate_json(json_data)

                for msg in parsed_messages:
                    # Extract content properly from pydantic-ai message structures
                    if hasattr(msg, "parts") and msg.parts:
                        content_parts = []
                        sender_name = "unknown"

                        for part in msg.parts:
                            if hasattr(part, "content"):
                                part_content = part.content
                                # Extract sender name from user-prompt content (format: "Sender: message")
                                if (
                                    hasattr(part, "part_kind")
                                    and part.part_kind == "user-prompt"
                                    and ":" in part_content
                                ):
                                    sender_part, message_part = part_content.split(
                                        ":", 1
                                    )
                                    sender_name = sender_part.strip()
                                    content_parts.append(message_part.strip())
                                # Extract agent name from system prompt
                                elif (
                                    hasattr(part, "part_kind")
                                    and part.part_kind == "system-prompt"
                                ):
                                    # Look for "You are [Name]" pattern in system prompt
                                    if "You are " in part_content:
                                        lines = part_content.split("\n")
                                        for line in lines:
                                            if line.strip().startswith("You are "):
                                                agent_name = (
                                                    line.replace("You are ", "")
                                                    .split(".")[0]
                                                    .strip()
                                                )
                                                if agent_name and agent_name not in [
                                                    "a",
                                                    "an",
                                                    "the",
                                                ]:
                                                    current_agent = agent_name
                                                    break
                                    content_parts.append(part_content)
                                else:
                                    content_parts.append(part_content)
                            elif (
                                hasattr(part, "part_kind") and part.part_kind == "text"
                            ):
                                content_parts.append(str(part))

                        content = (
                            "\n".join(content_parts) if content_parts else str(msg)
                        )
                    else:
                        content = getattr(msg, "content", str(msg))
                        sender_name = "unknown"

                    # Determine role/sender from message kind and structure
                    if hasattr(msg, "kind"):
                        if msg.kind == "request":
                            role = sender_name if sender_name != "unknown" else "user"
                        elif msg.kind == "response":
                            # Use the current agent name we extracted from system prompt
                            role = current_agent
                        else:
                            role = getattr(msg, "role", msg.kind)
                    else:
                        role = getattr(msg, "role", "unknown")

                    messages.append(
                        {
                            "role": role,
                            "content": content,
                            "timestamp": getattr(msg, "timestamp", None),
                            "type": "history",
                        }
                    )
            except Exception as e:
                print(f"Error parsing message history: {e}")

        return messages

    except Exception as e:
        print(f"Error getting chat messages for topic {topic}: {e}")
        return []


async def export_chat_to_markdown(topic: str, output_file: str = None) -> str:
    """
    Export chat messages to markdown format.

    Args:
        topic: The chat topic/channel name
        output_file: Optional file path to save the markdown (if None, returns string)

    Returns:
        Markdown formatted string of the chat
    """
    try:
        messages = await get_chat_messages(topic)

        # Create markdown content
        markdown_lines = [
            f"# Chat: {topic}",
            "",
            f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Messages:** {len(messages)}",
            "",
            "---",
            "",
        ]

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")

            # Format timestamp if available
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    f" _{dt.strftime('%H:%M:%S')}_"
                except:
                    pass

            # Add message to markdown in "**sender** content" format
            sender_name = role.title() if role in ["user", "assistant"] else role
            markdown_lines.extend([f"**{sender_name}** {content}", ""])

        markdown_content = "\n".join(markdown_lines)

        # Save to file if specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

        return markdown_content

    except Exception as e:
        error_msg = f"Error exporting chat to markdown for topic {topic}: {e}"
        print(error_msg)
        return f"# Error\n\n{error_msg}"


async def export_chat_to_dict(topic: str) -> dict[str, Any]:
    """
    Export complete chat data for a topic including metadata.

    Args:
        topic: The chat topic/channel name

    Returns:
        Dictionary containing all chat data and metadata
    """
    try:
        messages = await get_chat_messages(topic)

        return {
            "topic": topic,
            "message_count": len(messages),
            "export_timestamp": datetime.now().isoformat(),
            "messages": messages,
        }

    except Exception as e:
        print(f"Error exporting chat for topic {topic}: {e}")
        return {"topic": topic, "error": str(e), "messages": []}
