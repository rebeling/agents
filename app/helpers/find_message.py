import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.redis import redis_client
from app.helpers.dialogues import list_chat_topics


async def find_dominique_message():
    """Find the specific Dominique message in Redis data"""

    topics = await list_chat_topics()
    target_text = "Hello. I'm Dominique, a philosophical strategist and cultural critic"

    for topic in topics:
        print(f"\n=== Searching in topic: {topic} ===")
        history_key = f"{topic}_history"
        raw_entries = await redis_client.lrange(history_key, 0, -1)

        for i, entry in enumerate(raw_entries):
            try:
                if isinstance(entry, bytes):
                    entry = entry.decode("utf-8")

                # Check if target text is in this entry
                if target_text in entry:
                    print(f"\nFOUND in entry {i}!")
                    print("Raw Redis data:")
                    print(entry)
                    print("\nParsed structure:")
                    parsed = json.loads(entry)
                    print(json.dumps(parsed, indent=2))
                    return

            except Exception as e:
                print(f"Error parsing entry {i}: {e}")

    print("Message not found in any topic")


if __name__ == "__main__":
    asyncio.run(find_dominique_message())
