"""Parser for ChatGPT export JSON (conversations.json).

Handles the ChatGPT data export format where each conversation contains
a linear mapping of message nodes. The export file is typically named
`conversations.json` from a ChatGPT data export request.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class ParsedMessage:
    """Represents a single parsed message from ChatGPT export."""

    def __init__(
        self,
        message_id: str,
        role: str,
        content: str,
        create_time: datetime | None,
    ) -> None:
        self.message_id = message_id
        self.role = role
        self.content = content
        self.create_time = create_time


class ParsedConversation:
    """Represents a single parsed conversation from ChatGPT export."""

    def __init__(
        self,
        conversation_id: str,
        title: str,
        create_time: datetime | None,
        messages: list[ParsedMessage],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.conversation_id = conversation_id
        self.title = title
        self.create_time = create_time
        self.messages = messages
        self.metadata = metadata or {}


def _normalize_role(role: str) -> str:
    """Normalize role string to lower-case standard form.

    ChatGPT export may use various role casing (e.g., 'user', 'USER', 'User').
    """
    return role.lower().strip()


def _extract_message_content(message_node: dict) -> str:
    """Extract text content from a message node.

    ChatGPT export stores content in different structures depending on type:
    - Simple text: {'parts': ['text content']}
    - Multimodal: {'parts': [{'content_type': 'text', ...}]}
    """
    content = message_node.get("content", {})
    if isinstance(content, str):
        return content

    parts = content.get("parts", []) if isinstance(content, dict) else []
    text_parts: list[str] = []

    for part in parts:
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict):
            text_parts.append(part.get("text", "") or "")
        elif isinstance(part, list):
            # Some nested arrays contain text
            for sub in part:
                if isinstance(sub, str):
                    text_parts.append(sub)

    return "\n".join(text_parts).strip()


def _parse_mapping_node(
    node_id: str,
    node: dict,
) -> ParsedMessage | None:
    """Parse a single node from the conversation mapping.

    Returns None for non-leaf nodes (folders, etc.) or nodes without messages.
    """
    message_data = node.get("message")
    if not message_data:
        return None

    role = _normalize_role(message_data.get("role", ""))
    if role not in ("user", "assistant", "system"):
        return None

    content = _extract_message_content(message_data)
    if not content:
        return None

    create_time = message_data.get("create_time")
    parsed_time: datetime | None = None
    if create_time is not None and isinstance(create_time, (int, float)):
        parsed_time = datetime.fromtimestamp(create_time, tz=timezone.utc)

    return ParsedMessage(
        message_id=node_id,
        role=role,
        content=content,
        create_time=parsed_time,
    )


def parse_conversations(file_path: str) -> list[ParsedConversation]:
    """Parse a ChatGPT export conversations.json file.

    Args:
        file_path: Path to the conversations.json file.

    Returns:
        A list of ParsedConversation objects.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValueError: If the JSON is not in the expected format.
    """
    logger.info("Parsing ChatGPT export file: %s", file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "Expected a JSON array of conversations at the top level, "
            f"got {type(data).__name__}"
        )

    conversations: list[ParsedConversation] = []
    skipped = 0

    for conv_index, conv in enumerate(data):
        if not isinstance(conv, dict):
            logger.warning("Skipping non-dict item at index %d", conv_index)
            skipped += 1
            continue

        conversation_id = conv.get("conversation_id", f"index_{conv_index}")
        title = conv.get("title", "") or ""
        create_time = conv.get("create_time")
        parsed_time: datetime | None = None
        if create_time is not None and isinstance(create_time, (int, float)):
            parsed_time = datetime.fromtimestamp(create_time, tz=timezone.utc)

        mapping = conv.get("mapping")
        if not isinstance(mapping, dict):
            logger.debug(
                "Skipping conversation '%s': no valid mapping found", title
            )
            skipped += 1
            continue

        # Collect all messages from the mapping tree, then sort by create_time
        raw_messages: list[ParsedMessage] = []

        for node_id, node in mapping.items():
            if not isinstance(node, dict):
                continue
            msg = _parse_mapping_node(str(node_id), node)
            if msg is not None:
                raw_messages.append(msg)

        # Sort messages by create_time, falling back to message_id for stable order
        raw_messages.sort(
            key=lambda m: (m.create_time or datetime.min.replace(tzinfo=timezone.utc), m.message_id)
        )

        # Assign sequential sequence numbers
        for seq_idx, msg in enumerate(raw_messages, start=1):
            msg.sequence = seq_idx  # type: ignore[attr-defined]

        # Add sequence to each message object for convenience
        class _OrderedMessage(ParsedMessage):
            def __init__(
                self,
                msg: ParsedMessage,
                sequence: int,
            ) -> None:
                # Copy all fields
                super().__init__(
                    msg.message_id, msg.role, msg.content, msg.create_time
                )
                self.sequence = sequence

        ordered_messages = [
            _OrderedMessage(m, idx + 1)
            for idx, m in enumerate(raw_messages)
        ]

        conversations.append(
            ParsedConversation(
                conversation_id=conversation_id,
                title=title,
                create_time=parsed_time,
                messages=ordered_messages,
                metadata={
                    "source_conversation_id": conversation_id,
                },
            )
        )

        logger.debug(
            "Parsed conversation '%s': %d messages",
            title or "(untitled)",
            len(ordered_messages),
        )

    logger.info(
        "Parsed %d conversations from %s (skipped %d items)",
        len(conversations),
        file_path,
        skipped,
    )

    return conversations
