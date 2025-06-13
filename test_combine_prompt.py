#!/usr/bin/env python3
"""
Test file for the combine_prompt function in app.utils.

This test file validates the combine_prompt function with various input scenarios
to ensure it properly combines meta prompts, agent configurations, and patterns.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from app.utils import combine_prompt


class TestCombinePrompt:
    """Test class for the combine_prompt function."""

    def test_combine_prompt_with_meta_prompt_only(self):
        """Test combining when only meta prompt is provided."""
        registry_meta = {
            "prompt": "You are a helpful AI assistant.",
            "patterns": ["Today is {today}.", "Be concise."],
        }

        agent_config = {
            "name": "TestAgent",
            "system_prompt": "You are TestAgent. Follow instructions carefully.",
        }

        expected_output = (
            "You are a helpful AI assistant.\n"
            "Today is {today}.\n"
            "Be concise.\n\n"
            "You are TestAgent. Follow instructions carefully."
        )

        result = combine_prompt(registry_meta, agent_config)
        assert result == expected_output

    def test_combine_prompt_with_agent_meta_prompt(self):
        """Test combining when agent has its own meta_prompt."""
        registry_meta = {
            "prompt": "Global instructions.",
            "patterns": ["Pattern 1", "Pattern 2"],
        }

        agent_config = {
            "name": "TestAgent",
            "meta_prompt": "Agent specific instructions.",
            "system_prompt": "Main system prompt.",
        }

        expected_output = (
            "Global instructions.\n"
            "Pattern 1\n"
            "Pattern 2\n\n"
            "Agent specific instructions.\n\n"
            "Main system prompt."
        )

        result = combine_prompt(registry_meta, agent_config)
        assert result == expected_output

    def test_combine_prompt_with_agent_patterns(self):
        """Test combining when agent has its own patterns."""
        registry_meta = {"prompt": "Global prompt.", "patterns": ["Global pattern"]}

        agent_config = {
            "name": "TestAgent",
            "patterns": ["Agent pattern 1", "Agent pattern 2"],
            "system_prompt": "System prompt.",
        }

        expected_output = (
            "Global prompt.\n"
            "Global pattern\n\n"
            "Patterns to follow:\n"
            "- Agent pattern 1\n"
            "- Agent pattern 2\n\n"
            "System prompt."
        )

        result = combine_prompt(registry_meta, agent_config)
        assert result == expected_output

    def test_combine_prompt_no_meta_or_patterns(self):
        """Test combining when no meta or patterns are provided."""
        registry_meta = {}

        agent_config = {"name": "TestAgent", "system_prompt": "Simple system prompt."}

        expected_output = "Simple system prompt."

        result = combine_prompt(registry_meta, agent_config)
        assert result == expected_output

    def test_combine_prompt_empty_system_prompt(self):
        """Test combining when system_prompt is empty."""
        registry_meta = {"prompt": "Meta prompt.", "patterns": ["Pattern 1"]}

        agent_config = {"name": "TestAgent", "system_prompt": ""}

        expected_output = "Meta prompt.\nPattern 1"

        result = combine_prompt(registry_meta, agent_config)
        assert result == expected_output

    def test_combine_prompt_malformed_system_prompt_key(self):
        """Test handling of malformed system_prompt key (like 'system_prompt"')."""
        registry_meta = {"prompt": "Meta prompt."}

        agent_config = {
            "name": "TestAgent",
            'system_prompt"': "Malformed key system prompt.",  # Note the extra quote
            "system_prompt": "Normal key system prompt.",
        }

        expected_output = "Meta prompt.\n\nNormal key system prompt."

        result = combine_prompt(registry_meta, agent_config)
        assert result == expected_output

    def test_combine_prompt_with_today_pattern(self):
        """Test that today's date pattern is handled correctly."""
        registry_meta = {
            "prompt": "System message.",
            "patterns": ["Today is {today}.", "Be helpful."],
        }

        agent_config = {"name": "TestAgent", "system_prompt": "You are TestAgent."}

        result = combine_prompt(registry_meta, agent_config)

        # Check that the pattern is included
        assert "Today is {today}." in result
        assert "Be helpful." in result
        assert "System message." in result
        assert "You are TestAgent." in result

    def test_combine_prompt_complex_scenario(self):
        """Test a complex scenario with all components."""
        registry_meta = {
            "prompt": "- Speak short like in a chat\n- Never mention being an AI assistant.",
            "patterns": ["Today is {today}.", "Max tokens: {MAX_RESPONSE_TOKENS}"],
        }

        agent_config = {
            "name": "Dominique",
            "meta_prompt": "Additional agent instructions.",
            "patterns": ["Be philosophical", "Think critically"],
            "system_prompt": (
                "You are Dominique.\n"
                "Keep your answers short, concise and insightful.\n"
                "Role: Philosophical Strategist"
            ),
        }

        result = combine_prompt(registry_meta, agent_config)

        # Verify all components are present
        assert "Speak short like in a chat" in result
        assert "Never mention being an AI assistant" in result
        assert "Today is {today}." in result
        assert "Max tokens: {MAX_RESPONSE_TOKENS}" in result
        assert "Additional agent instructions" in result
        assert "Be philosophical" in result
        assert "Think critically" in result
        assert "You are Dominique" in result
        assert "Philosophical Strategist" in result

    @patch("app.utils.sys.modules")
    def test_combine_prompt_with_max_tokens_import(self, mock_modules):
        """Test that MAX_RESPONSE_TOKENS is properly imported."""
        # Mock the specs module
        mock_specs = MagicMock()
        mock_specs.MAX_RESPONSE_TOKENS = 200
        mock_modules.get.return_value = mock_specs

        registry_meta = {"patterns": ["Max tokens: {MAX_RESPONSE_TOKENS}"]}

        agent_config = {"system_prompt": "Test prompt"}

        combine_prompt(registry_meta, agent_config)

        # The function should attempt to get MAX_RESPONSE_TOKENS
        mock_modules.get.assert_called_with("app.specs", None)


def test_input_output_examples():
    """Test function with real-world input/output examples."""

    # Example 1: Simple agent configuration
    registry_meta_1 = {
        "prompt": "- Speak short like in a chat\n- Never mention being a language model or AI assistant.",
        "patterns": ["Today is {today}.", "Max tokens: {MAX_RESPONSE_TOKENS}"],
    }

    agent_config_1 = {
        "name": "Ada",
        "system_prompt": (
            "You are Ada.\n"
            "Keep your answers concise, precise, and insightful.\n"
            "Role: Analytical Thinker and Curious Coder"
        ),
    }

    result_1 = combine_prompt(registry_meta_1, agent_config_1)

    expected_1 = (
        "- Speak short like in a chat\n"
        "- Never mention being a language model or AI assistant.\n"
        "Today is {today}.\n"
        "Max tokens: {MAX_RESPONSE_TOKENS}\n\n"
        "You are Ada.\n"
        "Keep your answers concise, precise, and insightful.\n"
        "Role: Analytical Thinker and Curious Coder"
    )

    assert result_1 == expected_1

    # Example 2: Agent with own patterns
    registry_meta_2 = {"prompt": "Global instructions."}

    agent_config_2 = {
        "name": "Giulio",
        "patterns": ["Use artistic metaphors", "Be creative"],
        "system_prompt": "You are Giulio, a creative advisor.",
    }

    result_2 = combine_prompt(registry_meta_2, agent_config_2)

    expected_2 = (
        "Global instructions.\n\n"
        "Patterns to follow:\n"
        "- Use artistic metaphors\n"
        "- Be creative\n\n"
        "You are Giulio, a creative advisor."
    )

    assert result_2 == expected_2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
