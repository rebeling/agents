#!/usr/bin/env python3
"""Simple export script to replace the deleted helpers/export_dialogues.py"""

import asyncio
from pathlib import Path

from app.core.redis_export import export_topic_to_markdown, list_chat_topics


async def export_all_dialogues():
    """Export all Redis chat topics to markdown files."""
    topics = await list_chat_topics()
    export_dir = Path("agent-dialogues")
    export_dir.mkdir(exist_ok=True)

    for topic in topics:
        markdown_content = await export_topic_to_markdown(topic)
        file_path = export_dir / f"{topic}.md"

        with open(file_path, "w") as f:
            f.write(markdown_content)

        print(f"Exported {topic} to {file_path}")

    print(f"Exported {len(topics)} topics to {export_dir}")


if __name__ == "__main__":
    asyncio.run(export_all_dialogues())
