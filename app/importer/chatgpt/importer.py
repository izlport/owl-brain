"""Importer that writes parsed ChatGPT conversations into the database."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session
from app.importer.chatgpt.parser import parse_conversations
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.source import KnowledgeSource

logger = logging.getLogger(__name__)


async def _create_source(
    session: AsyncSession,
    file_path: str,
) -> KnowledgeSource:
    """Create or retrieve a KnowledgeSource for the import file."""
    stmt = select(KnowledgeSource).where(
        KnowledgeSource.file_path == file_path,
        KnowledgeSource.source_type == "chatgpt_export",
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        logger.info("Found existing source record for: %s", file_path)
        return existing

    source = KnowledgeSource(
        source_type="chatgpt_export",
        name=f"ChatGPT Export: {file_path}",
        file_path=file_path,
        metadata_={
            "imported_at": datetime.now(tz=timezone.utc).isoformat(),
        },
    )
    session.add(source)
    await session.flush()
    logger.info("Created source record: %s (%s)", source.id, file_path)
    return source


def _convert_parsed_time(parsed_time: datetime | None) -> datetime:
    """Convert an optional parsed time to a datetime (default to now in UTC)."""
    if parsed_time is not None:
        return parsed_time
    return datetime.now(tz=timezone.utc)


async def import_conversations(file_path: str) -> dict[str, int]:
    """Parse a ChatGPT export file and import all conversations into the database.

    Args:
        file_path: Path to the conversations.json file.

    Returns:
        A dict with counts: {conversations: int, messages: int}.
    """
    # Step 1: Parse the file
    parsed_convos = parse_conversations(file_path)
    logger.info(
        "Parsed %d conversations, starting database import...",
        len(parsed_convos),
    )

    # Step 2: Persist to database
    async with async_session() as session:
        source = await _create_source(session, file_path)

        conv_count = 0
        msg_count = 0

        for parsed in parsed_convos:
            # Create conversation
            conv = Conversation(
                source_id=source.id,
                title=parsed.title or f"ChatGPT Conversation ({parsed.conversation_id})",
                summary=None,
                metadata_={
                    "source_conversation_id": parsed.conversation_id,
                    "parsed_at": datetime.now(tz=timezone.utc).isoformat(),
                },
            )
            session.add(conv)
            await session.flush()
            conv_count += 1

            # Create messages
            for parsed_msg in parsed.messages:
                msg = Message(
                    conversation_id=conv.id,
                    role=parsed_msg.role,
                    content=parsed_msg.content,
                    sequence=getattr(parsed_msg, "sequence", 0),
                )
                session.add(msg)
                msg_count += 1

            logger.debug(
                "Imported conversation '%s': %d messages",
                parsed.title or "(untitled)",
                len(parsed.messages),
            )

        await session.commit()

    logger.info(
        "Import complete: %d conversations, %d messages",
        conv_count,
        msg_count,
    )

    return {
        "conversations": conv_count,
        "messages": msg_count,
    }

