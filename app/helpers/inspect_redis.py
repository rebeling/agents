import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.redis import redis_client
from app.helpers.dialogues import list_chat_topics


async def show_redis_entries():
    """Show full Redis entries from different storage types"""

    # Get all available topics
    topics = await list_chat_topics()
    if not topics:
        print("No topics found")
        return

    topic = topics[0]  # Use first topic
    print(f"=== Redis entries for topic: {topic} ===\n")

    # 1. Show raw pub/sub message format (what gets published)
    print("1. Pub/Sub Message Format (what gets published):")
    sample_pubsub = {
        "content": "Hello, how are you today?",
        "sender": "Agent Rebel",
        "timestamp": "2025-06-13T14:30:25.123456",
        "role": "user",
    }
    print(json.dumps(sample_pubsub, indent=2))
    print()

    # 2. Show history storage format (ModelMessages JSON)
    print("2. History Storage Format (stored in Redis lists):")
    history_key = f"{topic}_history"
    raw_entries = await redis_client.lrange(history_key, 0, 2)  # Get first 3 entries

    for i, entry in enumerate(raw_entries):
        print(f"Entry {i + 1} (raw Redis data):")
        # Decode if bytes
        if isinstance(entry, bytes):
            entry = entry.decode("utf-8")
        print(entry)
        print()

        # Try to parse and show structure
        try:
            parsed = json.loads(entry)
            print(f"Entry {i + 1} (parsed structure):")
            if isinstance(parsed, list):
                for j, msg in enumerate(parsed):
                    print(f"  Message {j + 1}: {json.dumps(msg, indent=4)}")
            else:
                print(json.dumps(parsed, indent=2))
            print()
        except Exception as e:
            print(f"Could not parse entry {i + 1}: {e}\n")

    # 3. Show current Redis keys for this topic
    print("3. Redis Keys:")
    all_keys = await redis_client.keys(f"{topic}*")
    for key in all_keys:
        key_type = await redis_client.type(key)
        if key_type == "list":
            length = await redis_client.llen(key)
            print(f"  {key} (list, {length} items)")
        else:
            print(f"  {key} ({key_type})")


if __name__ == "__main__":
    asyncio.run(show_redis_entries())
