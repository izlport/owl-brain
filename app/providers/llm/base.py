"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for LLM text generation.

    All LLM providers (DeepSeek, OpenAI, etc.) must implement this interface.
    """

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the generated text response.

        Args:
            prompt: The full prompt string to send to the model.

        Returns:
            The generated text response from the LLM.

        Raises:
            LLMProviderError: If the API call fails or returns an error.
        """
        ...
