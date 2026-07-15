"""Knowledge extractor that uses an LLM to extract structured knowledge from conversations."""

import json
import logging
import re
from typing import Any

from app.extractor.prompt import KNOWLEDGE_EXTRACTION_PROMPT
from app.models.message import Message
from app.providers.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class ExtractedKnowledge:
    """Result from the knowledge extraction process."""

    def __init__(
        self,
        title: str,
        category: str,
        summary: str,
        content: str,
        tags: list[str],
    ) -> None:
        self.title = title
        self.category = category
        self.summary = summary
        self.content = content
        self.tags = tags


def _build_chat_text(messages: list[Message]) -> str:
    """Convert a list of Message ORM objects into a formatted chat text.

    Args:
        messages: List of Message objects, expected to be ordered by sequence.

    Returns:
        Formatted string like "user: ...\\nassistant: ...\\nuser: ..."
    """
    lines: list[str] = []
    for msg in messages:
        lines.append(f"{msg.role}: {msg.content}")
    return "\n\n".join(lines)


def _parse_json_response(raw: str) -> dict[str, Any]:
    """Parse a JSON response from the LLM, handling markdown fences.

    The LLM may wrap JSON in ```json ... ``` fences. This function
    strips them before parsing.

    Args:
        raw: Raw response string from the LLM.

    Returns:
        Parsed JSON dictionary.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
    """
    # Strip markdown code fences if present
    cleaned = raw.strip()
    # Remove ```json ... ``` fences
    cleaned = re.sub(
        r"^```(?:json)?\s*\n?(.*?)\n?```\s*$",
        r"\1",
        cleaned,
        flags=re.DOTALL,
    )
    # Remove single backtick fences
    cleaned = re.sub(
        r"^```(.*?)```\s*$",
        r"\1",
        cleaned,
        flags=re.DOTALL,
    )
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM response as JSON: %s", exc)
        logger.debug("Raw response: %s", raw)
        raise ValueError(
            f"Failed to parse LLM response as JSON: {exc}"
        ) from exc


def _validate_extracted(data: dict[str, Any]) -> None:
    """Validate the extracted JSON has all required fields.

    Args:
        data: Parsed JSON dictionary from the LLM.

    Raises:
        ValueError: If required fields are missing or have wrong types.
    """
    required_fields = ["title", "category", "summary", "content", "tags"]
    for field in required_fields:
        if field not in data:
            raise ValueError(
                f"Missing required field '{field}' in LLM response"
            )

    if not isinstance(data["title"], str) or not data["title"].strip():
        raise ValueError("Field 'title' must be a non-empty string")
    if not isinstance(data["category"], str) or not data["category"].strip():
        raise ValueError("Field 'category' must be a non-empty string")
    if not isinstance(data["summary"], str) or not data["summary"].strip():
        raise ValueError("Field 'summary' must be a non-empty string")
    if not isinstance(data["content"], str) or not data["content"].strip():
        raise ValueError("Field 'content' must be a non-empty string")
    if not isinstance(data["tags"], list):
        raise ValueError("Field 'tags' must be a list")
    for tag in data["tags"]:
        if not isinstance(tag, str):
            raise ValueError("Each tag must be a string")


async def extract_knowledge(
    messages: list[Message],
    llm_provider: LLMProvider | None = None,
) -> ExtractedKnowledge:
    """Extract structured knowledge from a list of conversation messages.

    The function:
        1. Formats messages into a chat text
        2. Builds the extraction prompt
        3. Calls the LLM
        4. Parses and validates the JSON response
        5. Returns an ExtractedKnowledge object

    Args:
        messages: List of Message objects ordered by sequence.
        llm_provider: An LLM provider instance. If None, a default provider
                      will be created via the factory.

    Returns:
        An ExtractedKnowledge object with title, category, summary,
        content, and tags.

    Raises:
        ValueError: If the LLM response cannot be parsed or validated.
    """
    if llm_provider is None:
        from app.providers import get_llm_provider

        llm_provider = get_llm_provider()

    # Build chat text from messages
    chat_text = _build_chat_text(messages)
    logger.debug(
        "Extracting knowledge from %d messages (%d chars)",
        len(messages),
        len(chat_text),
    )

    # Build prompt
    prompt = KNOWLEDGE_EXTRACTION_PROMPT.format(chat_text=chat_text)

    # Call LLM
    raw_response = await llm_provider.generate(prompt)
    logger.debug("LLM response received (%d chars)", len(raw_response))

    # Parse and validate
    data = _parse_json_response(raw_response)
    _validate_extracted(data)

    result = ExtractedKnowledge(
        title=data["title"].strip(),
        category=data["category"].strip(),
        summary=data["summary"].strip(),
        content=data["content"].strip(),
        tags=[t.strip().lower() for t in data["tags"]],
    )

    logger.info(
        "Extracted knowledge: title='%s', category='%s', %d tags",
        result.title,
        result.category,
        len(result.tags),
    )

    return result
