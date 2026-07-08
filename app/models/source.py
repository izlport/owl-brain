import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class KnowledgeSource(Base):
    """Represents a source of imported data (e.g., ChatGPT export file)."""

    __tablename__ = "knowledge_source"

    source_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="e.g., chatgpt_export, manual_input"
    )
    name: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="Human-readable name of the source"
    )
    file_path: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Original file path or identifier"
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, comment="Arbitrary source metadata"
    )

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="source", cascade="all, delete-orphan"
    )
