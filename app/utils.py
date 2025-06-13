import colorsys
import hashlib
import sys
from datetime import datetime
from pathlib import Path

import yaml

today = datetime.now().strftime("%B %d, %Y")


def combine_prompt(registry_meta, agent_config):
    """
    Combine registry meta information with agent configuration to create a complete prompt.

    Args:
        registry_meta: Meta configuration from agent registry (contains prompt and patterns)
        agent_config: Individual agent configuration (contains system_prompt, meta_prompt, patterns)

    Returns:
        str: Combined prompt string
    """
    MAX_RESPONSE_TOKENS = getattr(
        sys.modules.get("app.specs", None),
        "MAX_RESPONSE_TOKENS",
        150,
    )

    # Start building the combined prompt
    prompt_parts = []

    # Add registry meta prompt and patterns
    if registry_meta:
        if "prompt" in registry_meta:
            prompt_parts.append(registry_meta["prompt"])

        if "patterns" in registry_meta:
            for pattern in registry_meta["patterns"]:
                # Format patterns with available variables, handle formatting errors
                try:
                    formatted_pattern = pattern.format(
                        today=today, MAX_RESPONSE_TOKENS=MAX_RESPONSE_TOKENS
                    )
                    prompt_parts.append(formatted_pattern)
                except (ValueError, KeyError):
                    # If formatting fails, use pattern as-is
                    prompt_parts.append(pattern)

    # Add agent-specific meta prompt
    agent_meta_prompt = agent_config.get("meta_prompt", "")
    if agent_meta_prompt:
        prompt_parts.append(agent_meta_prompt)

    # Add agent-specific patterns
    agent_patterns = agent_config.get("patterns", [])
    if agent_patterns:
        patterns_text = "Patterns to follow:\n" + "\n".join(
            f"- {pattern}" for pattern in agent_patterns
        )
        prompt_parts.append(patterns_text)

    # Add the main system prompt
    system_prompt = agent_config.get("system_prompt", "")
    # Handle malformed keys like 'system_prompt"'
    if not system_prompt and 'system_prompt"' in agent_config:
        system_prompt = agent_config['system_prompt"']

    if system_prompt:
        prompt_parts.append(system_prompt)

    # Join all parts with double newlines
    combined_prompt = "\n\n".join(part for part in prompt_parts if part.strip())

    return combined_prompt


def load_agent_registry() -> dict:
    """Load the agent registry YAML file."""
    registry_path = Path(__file__).parent.parent / "app" / "agent_registry.yml"
    with open(registry_path) as f:
        return yaml.safe_load(f)


def name_to_pastel_hex(name: str) -> str:
    """Generate a consistent pastel HEX color for a given name string."""
    # Hash the name and convert to an integer
    name_hash = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)

    # Use the hash to determine the hue (0–360)
    hue = name_hash % 360

    # Fixed pastel saturation and lightness
    saturation = 0.7  # as a float (70%)
    lightness = 0.85  # as a float (85%)

    # Convert HSL to RGB (colorsys uses H, L, S in 0..1 range)
    h = hue / 360
    r, g, b = colorsys.hls_to_rgb(h, lightness, saturation)

    # Convert RGB (0..1) to HEX
    r_hex = int(r * 255)
    g_hex = int(g * 255)
    b_hex = int(b * 255)

    return f"#{r_hex:02x}{g_hex:02x}{b_hex:02x}"
