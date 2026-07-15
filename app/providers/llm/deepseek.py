"""DeepSeek LLM provider implementation using the OpenAI-compatible SDK."""

import logging

from openai import AsyncOpenAI

from app.config.settings import settings
from app.providers.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """LLM provider for DeepSeek API via OpenAI-compatible interface.

    Uses the OpenAI SDK with a custom base_url pointing to DeepSeek's API.
    Configuration is loaded from settings:

        - DEEPSEEK_API_KEY: API key for authentication
        - DEEPSEEK_MODEL: Model name (default: deepseek-chat)
    """

    def __init__(self) -> None:
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            logger.warning(
                "DEEPSEEK_API_KEY is not set. "
                "Set it in .env or environment variables."
            )

        self._model = settings.DEEPSEEK_MODEL or "deepseek-chat"
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    async def generate(self, prompt: str) -> str:
        """Send a prompt to DeepSeek Chat and return the response text.

        Args:
            prompt: The full prompt string.

        Returns:
            Generated text content from the model.

        Raises:
            openai.APIError: If the DeepSeek API call fails.
        """
        logger.debug(
            "Sending request to DeepSeek model '%s' (%d chars)",
            self._model,
            len(prompt),
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        result = response.choices[0].message.content or ""
        logger.debug(
            "Received response from DeepSeek (%d chars)", len(result)
        )
        return result
