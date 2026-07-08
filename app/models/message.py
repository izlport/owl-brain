import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Message(Base):
    """A single message within a conversation."""

    __tablename__ = "message"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="e.g., user, assistant, system"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Message content"
    )
    sequence: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Order within the conversation"
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
