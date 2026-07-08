import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Conversation(Base):
    """Represents a single conversation (e.g., a ChatGPT thread)."""

    __tablename__ = "conversation"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_source.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="Conversation title"
    )
    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="AI-generated summary of the conversation"
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, comment="Conversation metadata"
    )

    # Relationships
    source: Mapped["KnowledgeSource"] = relationship(
        "KnowledgeSource", back_populates="conversations"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    knowledge: Mapped[list["Knowledge"]] = relationship(
        "Knowledge", back_populates="conversation"
    )
