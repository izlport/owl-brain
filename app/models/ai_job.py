from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AIJob(Base):
    """Tracks an AI job (extraction, summarization, embedding, etc.)."""

    __tablename__ = "ai_job"

    job_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="e.g., knowledge_extraction, summarization, embedding"
    )
    provider: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="e.g., deepseek, openai, bge"
    )
    model: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Model name used"
    )
    input_tokens: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="Input token count"
    )
    output_tokens: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="Output token count"
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        comment="pending, running, completed, failed",
    )
    error: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Error message if failed"
    )
