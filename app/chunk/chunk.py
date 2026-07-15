"""Chunk data class — a self-contained piece of text from a Knowledge item.

This is a pure Python data class, not a database ORM model.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class Chunk:
    """A single text chunk extracted from a Knowledge item.

    Attributes:
        knowledge_id: UUID of the parent Knowledge item.
        chunk_index: Zero-based sequential index within the parent.
        content: The text content of this chunk.
        token_count: Approximate number of tokens (chars / 4).
        metadata: Arbitrary metadata dict (e.g. source title, category).
    """

    knowledge_id: UUID
    chunk_index: int
    content: str
    token_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
