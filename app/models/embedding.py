import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Embedding(Base):
    """Vector embedding for a knowledge chunk, stored in pgvector."""

    __tablename__ = "embedding"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_chunk.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Embedding model name"
    )
    dimension: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Vector dimension"
    )
    vector: Mapped[list[float]] = mapped_column(
        Vector(1024),
        nullable=False,
        comment="pgvector embedding (up to 1024 dimensions)",
    )

    # Relationships
    chunk: Mapped["KnowledgeChunk"] = relationship(
        "KnowledgeChunk", back_populates="embeddings"
    )
