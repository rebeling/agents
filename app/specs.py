import json
from datetime import date, datetime

import redis.asyncio as redis
from decouple import config
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider

# Set today's date string
today = date.today().isoformat()  # returns "2025-06-02" if run on that day

# # see https://ai.pydantic.dev/models/openai/#example-local-usage
model_name = "llama3.2"
ollama_model = OpenAIModel(
    model_name=model_name,
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
#agent_model = ollama_model

# !beware openrouter docs are incorrect for pydantic
# see https://ai.pydantic.dev/models/openai/#openrouter
# and for models see https://openrouter.ai/models

model_name = "google/gemma-3-1b-it:free"
# model_name = "nousresearch/deephermes-3-mistral-24b-preview:free"
#model_name = "deepseek/deepseek-r1-0528-qwen3-8b:free"

openrouter_model = OpenAIModel(
    model_name=model_name,
    provider=OpenRouterProvider(api_key=config("OPENROUTER_API_KEY")),
)
agent_model = openrouter_model


# Format Redis channel name
# Replace slashes and colons to avoid Redis or system issues
sanitized_model_name = model_name.replace("/", "-").replace(":", "-")
REDIS_CHANNEL = f"chat-{today}-{sanitized_model_name}"

# Initialize Redis connection
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# works great with openrouter, but not with local ollama
MAX_RESPONSE_TOKENS = 100
model_settings = {"max_tokens": MAX_RESPONSE_TOKENS}


async def publish_to_redis(message):
    chat_message = {
        "content": message.content,
        "sender": "Agent Rebel",
        "timestamp": datetime.now().isoformat(),
        "role": "user",
    }
    json_chat_message = json.dumps(chat_message)
    await redis_client.publish(REDIS_CHANNEL, json_chat_message)
