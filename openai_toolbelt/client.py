"""Main client for interacting with the OpenAI API."""

import os
from typing import List, Optional, Union

import openai
import structlog
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from openai_toolbelt.models import ChatMessage, ChatResponse, OpenAIConfig

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """A client for interacting with the OpenAI API with additional features."""

    def __init__(
        self,
        config: Optional[OpenAIConfig] = None,
        profile: str = "default",
    ):
        """Initialize the OpenAI client.

        Args:
            config: Optional configuration object. If not provided, will load from environment.
            profile: Configuration profile to use (e.g., "dev", "prod").
        """
        load_dotenv()

        if config is None:
            config = OpenAIConfig(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                organization=os.getenv("OPENAI_ORGANIZATION"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

        self.config = config
        self.profile = profile
        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the OpenAI client with configuration."""
        openai.api_key = self.config.api_key
        if self.config.organization:
            openai.organization = self.config.organization
        if self.config.base_url:
            openai.base_url = self.config.base_url

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> Union[ChatResponse, List[ChatResponse]]:
        """Send a chat completion request to OpenAI.

        Args:
            messages: List of chat messages.
            model: Model to use. If not provided, uses default from config.
            temperature: Temperature for generation. If not provided, uses default from config.
            stream: Whether to stream the response.

        Returns:
            ChatResponse or list of ChatResponse if streaming.
        """
        model = model or self.config.default_model
        temperature = temperature or self.config.default_temperature

        logger.info(
            "sending_chat_request",
            model=model,
            message_count=len(messages),
            stream=stream,
        )

        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[msg.model_dump() for msg in messages],
                temperature=temperature,
                stream=stream,
            )

            if stream:
                return [
                    ChatResponse(
                        content=chunk.choices[0].delta.content or "",
                        model=model,
                        usage={},  # No usage info in streaming
                        cost_usd=0.0,  # Will calculate after completion
                        finish_reason=chunk.choices[0].finish_reason,
                    )
                    for chunk in response
                ]

            # Calculate cost (simplified version)
            cost_usd = self._calculate_cost(
                model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            )

            return ChatResponse(
                content=response.choices[0].message.content,
                model=model,
                usage=response.usage.model_dump(),
                cost_usd=cost_usd,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            logger.error(
                "chat_request_failed",
                error=str(e),
                model=model,
                message_count=len(messages),
            )
            raise

    def _calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Calculate the cost of a request in USD.

        Args:
            model: The model used.
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.

        Returns:
            Estimated cost in USD.
        """
        # Simplified pricing - you should update these with current rates
        pricing = {
            "gpt-3.5-turbo": (0.0015, 0.002),  # (prompt, completion) per 1K tokens
            "gpt-4": (0.03, 0.06),
            "gpt-4-turbo": (0.01, 0.03),
        }

        if model not in pricing:
            logger.warning("unknown_model_pricing", model=model)
            return 0.0

        prompt_cost = (prompt_tokens / 1000) * pricing[model][0]
        completion_cost = (completion_tokens / 1000) * pricing[model][1]

        return prompt_cost + completion_cost 