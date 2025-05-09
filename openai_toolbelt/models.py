"""Data models for the OpenAI Toolbelt."""

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Chat message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """A chat message with role and content."""

    role: Role
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from a chat completion."""

    content: str
    model: str
    usage: dict
    cost_usd: float = Field(..., description="Estimated cost in USD")
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[dict]] = None


class OpenAIConfig(BaseModel):
    """Configuration for the OpenAI client."""

    api_key: str = Field(..., description="OpenAI API key")
    organization: Optional[str] = Field(None, description="OpenAI organization ID")
    base_url: Optional[str] = Field(None, description="OpenAI API base URL")
    default_model: str = Field("gpt-3.5-turbo", description="Default model to use")
    default_temperature: float = Field(0.7, description="Default temperature")
    max_retries: int = Field(3, description="Maximum number of retries")
    timeout: int = Field(30, description="Request timeout in seconds") 