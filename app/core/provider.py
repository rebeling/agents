from decouple import config
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider

# # see https://ai.pydantic.dev/models/openai/#example-local-usage
model_name = "llama3.2"
ollama_model = OpenAIModel(
    model_name=model_name,
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
# agent_model = ollama_model

# !beware openrouter docs are incorrect for pydantic
# see https://ai.pydantic.dev/models/openai/#openrouter
# and for models see https://openrouter.ai/models

model_name = "google/gemma-3-1b-it:free"
# model_name = "nousresearch/deephermes-3-mistral-24b-preview:free"
# model_name = "deepseek/deepseek-r1-0528-qwen3-8b:free"

openrouter_model = OpenAIModel(
    model_name=model_name,
    provider=OpenRouterProvider(api_key=config("OPENROUTER_API_KEY")),
)
# agent_model = openrouter_model


claude_model = "claude-3-5-sonnet-latest"
# claude_model = 'claude-3-haiku-20240307'

anthropic_model = AnthropicModel(
    claude_model, provider=AnthropicProvider(api_key=config("ANTHROPIC_API_KEY"))
)
agent_model = anthropic_model


# works great with openrouter, but not with local ollama
MAX_RESPONSE_TOKENS = 100
model_settings = {"max_tokens": MAX_RESPONSE_TOKENS}

# Export for use in other modules
__all__ = ["agent_model", "model_settings", "MAX_RESPONSE_TOKENS"]
