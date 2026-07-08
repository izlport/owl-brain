import uuid

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Knowledge(Base):
    """Extracted knowledge unit — a coherent piece of information."""

    __tablename__ = "knowledge"

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="Knowledge title"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Full knowledge content"
    )
    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Short summary / abstract"
    )
    category: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="Category label"
    )
    importance: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Importance score (0.0 - 1.0)"
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, comment="Additional metadata"
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="knowledge"
    )
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk", back_populates="knowledge", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="knowledge_tag", back_populates="knowledge_items"
    )
