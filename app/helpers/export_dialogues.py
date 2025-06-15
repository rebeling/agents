import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.helpers.dialogues import export_chat_to_markdown, list_chat_topics


async def export_all_dialogues():
    """Export all chat topics to markdown files in the agent-dialogues folder"""

    # Get all available topics
    topics = await list_chat_topics()
    print(f"Found {len(topics)} topics to export")

    if not topics:
        print("No topics found to export")
        return

    # Ensure the dialogues directory exists
    output_dir = "agent-dialogues"
    os.makedirs(output_dir, exist_ok=True)

    # Export each topic
    for topic in topics:
        # Create safe filename from topic name
        filename = f"{topic}.md"
        filepath = os.path.join(output_dir, filename)

        try:
            await export_chat_to_markdown(topic, filepath)
            print(f"Exported: {topic} -> {filepath}")
        except Exception as e:
            print(f"Failed to export {topic}: {e}")


if __name__ == "__main__":
    asyncio.run(export_all_dialogues())
