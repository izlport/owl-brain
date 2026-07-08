import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tag(Base):
    """A tag / label for categorizing knowledge."""

    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="Tag name"
    )

    # Relationships
    knowledge_items: Mapped[list["Knowledge"]] = relationship(
        "Knowledge", secondary="knowledge_tag", back_populates="tags"
    )


class KnowledgeTag(Base):
    """Many-to-many relationship between Knowledge and Tag."""

    __tablename__ = "knowledge_tag"

    knowledge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    )
