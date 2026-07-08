import uuid

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class KnowledgeChunk(Base):
    """A chunk/section of a knowledge item, suitable for embedding."""

    __tablename__ = "knowledge_chunk"

    knowledge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Sequential index within the knowledge item"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Chunk text content"
    )
    token_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Approximate token count"
    )

    # Relationships
    knowledge: Mapped["Knowledge"] = relationship(
        "Knowledge", back_populates="chunks"
    )
    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding", back_populates="chunk", cascade="all, delete-orphan"
    )
