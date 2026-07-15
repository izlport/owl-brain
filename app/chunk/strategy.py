"""Chunk strategy definitions.

ChunkStrategy is an abstract interface for splitting text into smaller pieces.
DefaultChunkStrategy uses langchain-text-splitters' RecursiveCharacterTextSplitter.
"""

from abc import ABC, abstractmethod


class ChunkStrategy(ABC):
    """Abstract interface for text splitting strategies."""

    @abstractmethod
    def split(self, text: str) -> list[str]:
        """Split a single text into a list of chunk text strings.

        Args:
            text: The full text to split.

        Returns:
            A list of text fragments, ordered as they appeared in the original.
        """
        ...


class DefaultChunkStrategy(ChunkStrategy):
    """Default chunking strategy using RecursiveCharacterTextSplitter.

    Splits text recursively on paragraph breaks, then sentences, then
    character boundaries, keeping each chunk close to the target size.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
    ) -> None:
        """Initialise the splitter.

        Args:
            chunk_size:  Target characters per chunk (default 512).
            chunk_overlap: Overlap characters between consecutive chunks
                          (default 100).
        """
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

        # Lazy import to avoid hard dependency on langchain-text-splitters
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:
            raise ImportError(
                "DefaultChunkStrategy requires 'langchain-text-splitters'. "
                "Install it with: uv add langchain-text-splitters"
            ) from None

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, text: str) -> list[str]:
        """Split text into chunks using the configured splitter.

        Args:
            text: The full text to split.

        Returns:
            A list of chunk text strings.
        """
        if not text or not text.strip():
            return []

        return self._splitter.split_text(text)
