# OpenAI Toolbelt

> A batteries-included helper layer on top of the official [openai-python](https://github.com/openai/openai-python) SDK.

[![PyPI](https://img.shields.io/pypi/v/openai-toolbelt)](https://pypi.org/project/openai-toolbelt/)
[![License](https://img.shields.io/github/license/yourname/openai-toolbelt)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/openai-toolbelt)](pyproject.toml)

## ✨ Features

- **Centralized Configuration**: Manage API keys, organization IDs, and default settings
- **Automatic Retries**: Built-in exponential backoff and retry logic
- **Cost Tracking**: Automatic calculation of API costs per request
- **Structured Logging**: Detailed request/response logging with structlog
- **Type Safety**: Full type hints and Pydantic models
- **Streaming Support**: Easy handling of streaming responses
- **Environment Integration**: Seamless .env file support

## 🔧 Installation

```bash
pip install openai-toolbelt
```

## 🚀 Quick Start

```python
from openai_toolbelt import OpenAIClient, ChatMessage, Role

# Initialize client (automatically loads from environment variables)
client = OpenAIClient()

# Create a chat message
messages = [
    ChatMessage(role=Role.USER, content="Write a haiku about programming.")
]

# Send request
response = client.chat(messages)

# Print response
print(response.content)
print(f"Cost: ${response.cost_usd:.4f}")
```

## 🔑 Environment Variables

The client automatically loads these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_ORGANIZATION`: (Optional) Your OpenAI organization ID
- `OPENAI_BASE_URL`: (Optional) Custom API base URL

## 📚 API Reference

### OpenAIClient

The main client class for interacting with the OpenAI API.

```python
client = OpenAIClient(
    config=OpenAIConfig(
        api_key="your-api-key",
        organization="your-org-id",
        default_model="gpt-4",
        default_temperature=0.7,
    ),
    profile="prod"  # Optional profile name
)
```

### ChatMessage

A Pydantic model for chat messages:

```python
message = ChatMessage(
    role=Role.USER,
    content="Hello, world!",
    name="optional_name",
    tool_calls=None,
    tool_call_id=None
)
```

### ChatResponse

Response model containing:

- `content`: The generated text
- `model`: The model used
- `usage`: Token usage information
- `cost_usd`: Estimated cost in USD
- `finish_reason`: Why the generation finished
- `tool_calls`: Any tool calls made

## 🛠️ Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## 📝 License

Apache-2.0 - See [LICENSE](LICENSE) for details.
