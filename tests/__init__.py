"""
Test package for the agents application.

This package contains all test modules for testing the various components
of the agents application, including utility functions, agent configurations,
and the dynamic agent starter functionality.
"""

__version__ = "1.0.0"
__author__ = "Agents Team"

# Test configuration
TEST_CONFIG = {
    "test_data_dir": "test_data",
    "mock_agent_registry": "mock_agent_registry.yml",
    "default_timeout": 30,
    "test_ports": {"start": 9000, "end": 9099},
}

# Import commonly used test utilities
try:
    from .test_combine_prompt import TestCombinePrompt, TestCombinePromptExamples

    __all__ = ["TestCombinePrompt", "TestCombinePromptExamples", "TEST_CONFIG"]
except ImportError:
    # Handle case where test modules are not yet available
    __all__ = ["TEST_CONFIG"]
