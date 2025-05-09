"""Tests for the OpenAIClient class."""

import os
from unittest.mock import patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from openai_toolbelt import OpenAIClient, ChatMessage, Role
from openai_toolbelt.models import OpenAIConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return OpenAIConfig(
        api_key="test-key",
        organization="test-org",
        default_model="gpt-3.5-turbo",
        default_temperature=0.7,
    )


@pytest.fixture
def client(mock_config):
    """Create a client instance with mock config."""
    return OpenAIClient(config=mock_config)


def test_client_initialization(mock_config):
    """Test client initialization with config."""
    client = OpenAIClient(config=mock_config)
    assert client.config == mock_config
    assert client.profile == "default"


def test_client_initialization_from_env():
    """Test client initialization from environment variables."""
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "env-key",
            "OPENAI_ORGANIZATION": "env-org",
            "OPENAI_BASE_URL": "https://api.example.com",
        },
    ):
        client = OpenAIClient()
        assert client.config.api_key == "env-key"
        assert client.config.organization == "env-org"
        assert client.config.base_url == "https://api.example.com"


@patch("openai.chat.completions.create")
def test_chat_completion(mock_create, client):
    """Test chat completion request."""
    # Mock response
    mock_response = ChatCompletion(
        id="test-id",
        choices=[
            {
                "message": ChatCompletionMessage(
                    role="assistant",
                    content="Test response",
                ),
                "finish_reason": "stop",
                "index": 0,
            }
        ],
        created=1234567890,
        model="gpt-3.5-turbo",
        object="chat.completion",
        usage={
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
    )
    mock_create.return_value = mock_response

    # Test request
    messages = [ChatMessage(role=Role.USER, content="Test message")]
    response = client.chat(messages)

    # Verify response
    assert response.content == "Test response"
    assert response.model == "gpt-3.5-turbo"
    assert response.usage["prompt_tokens"] == 10
    assert response.usage["completion_tokens"] == 5
    assert response.cost_usd > 0  # Should calculate some cost

    # Verify API call
    mock_create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test message"}],
        temperature=0.7,
        stream=False,
    )


@patch("openai.chat.completions.create")
def test_chat_completion_streaming(mock_create, client):
    """Test streaming chat completion."""
    # Mock streaming response
    mock_chunks = [
        ChatCompletion(
            id="test-id",
            choices=[
                {
                    "delta": {"content": "Test"},
                    "finish_reason": None,
                    "index": 0,
                }
            ],
            created=1234567890,
            model="gpt-3.5-turbo",
            object="chat.completion.chunk",
        ),
        ChatCompletion(
            id="test-id",
            choices=[
                {
                    "delta": {"content": " response"},
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
            created=1234567890,
            model="gpt-3.5-turbo",
            object="chat.completion.chunk",
        ),
    ]
    mock_create.return_value = mock_chunks

    # Test request
    messages = [ChatMessage(role=Role.USER, content="Test message")]
    responses = client.chat(messages, stream=True)

    # Verify responses
    assert len(responses) == 2
    assert responses[0].content == "Test"
    assert responses[1].content == " response"
    assert all(r.model == "gpt-3.5-turbo" for r in responses)

    # Verify API call
    mock_create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test message"}],
        temperature=0.7,
        stream=True,
    ) 