"""Chunker — orchestrates splitting a Knowledge item into Chunk objects."""

import logging

from app.chunk.chunk import Chunk
from app.chunk.strategy import ChunkStrategy, DefaultChunkStrategy
from app.models.knowledge import Knowledge

logger = logging.getLogger(__name__)


def _estimate_token_count(text: str) -> int:
    """Estimate token count using a simple char / 4 heuristic.

    This is ~1.3× the actual OpenAI tiktoken count for English text,
    but is fast and dependency-free.  Can be swapped for a real tokenizer later.
    """
    return max(1, len(text) // 4)


class Chunker:
    """Splits a Knowledge ORM object into a list of Chunk data objects.

    Example::

        chunker = Chunker()
        chunks = chunker.split(knowledge)
    """

    def __init__(self, strategy: ChunkStrategy | None = None) -> None:
        """Initialise the chunker with an optional custom strategy.

        Args:
            strategy: A ChunkStrategy instance.  Defaults to DefaultChunkStrategy.
        """
        self._strategy = strategy or DefaultChunkStrategy()

    def split(self, knowledge: Knowledge) -> list[Chunk]:
        """Split a Knowledge item into Chunk objects.

        Args:
            knowledge: A SQLAlchemy Knowledge ORM instance.

        Returns:
            A list of Chunk objects, ordered by chunk_index ascending.
        """
        text = knowledge.content or ""
        if not text.strip():
            logger.warning(
                "Knowledge '%s' has empty content, returning no chunks.",
                knowledge.id,
            )
            return []

        fragments = self._strategy.split(text)
        chunks: list[Chunk] = []

        for idx, fragment in enumerate(fragments):
            chunk = Chunk(
                knowledge_id=knowledge.id,
                chunk_index=idx,
                content=fragment,
                token_count=_estimate_token_count(fragment),
                metadata={
                    "knowledge_title": knowledge.title or "",
                    "knowledge_category": knowledge.category or "",
                },
            )
            chunks.append(chunk)

        logger.debug(
            "Split knowledge '%s' (%d chars) into %d chunks.",
            knowledge.id,
            len(text),
            len(chunks),
        )
        return chunks

