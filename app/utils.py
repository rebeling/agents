import colorsys
import hashlib
import sys
from datetime import datetime
from pathlib import Path
from app.specs import MAX_RESPONSE_TOKENS
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
    # Start building the combined prompt
    the_prompt = []

    # Add the main system prompt
    system_prompt = agent_config["system_prompt"]
    the_prompt.append(system_prompt)

    # Add registry meta prompt and patterns
    if registry_meta:
        if "prompt" in registry_meta:
            the_prompt.append(registry_meta["prompt"])

        if "patterns" in registry_meta:
            # Format patterns with available variables, handle formatting errors
            formatted_pattern = registry_meta["patterns"].format(
                TODAY=today, MAX_RESPONSE_TOKENS=MAX_RESPONSE_TOKENS
            )
            the_prompt.append(formatted_pattern)

    # Join all parts with double newlines
    combined_prompt = "".join(the_prompt)
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
