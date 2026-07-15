"""Tests for the Knowledge Extractor.

These tests use a mock LLM provider to avoid calling the real DeepSeek API.
"""



import pytest

from app.extractor.knowledge_extractor import (
    ExtractedKnowledge,
    _build_chat_text,
    _parse_json_response,
    _validate_extracted,
    extract_knowledge,
)
from app.models.message import Message
from app.providers.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider that returns a configurable response."""

    def __init__(self, response: str = "") -> None:
        self.response = response
        self.last_prompt: str = ""
        self.call_count: int = 0

    async def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        self.call_count += 1
        return self.response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_messages() -> list[Message]:
    """Create sample Message objects simulating a Python async chat."""
    messages = []
    for i, (role, content) in enumerate(
        [
            (
                "user",
                "What is the best way to handle async tasks in Python?",
            ),
            (
                "assistant",
                "Use asyncio with async/await syntax. "
                "The asyncio.create_task() function is great "
                "for running concurrent tasks.",
            ),
            (
                "user",
                "Can you show me an example?",
            ),
            (
                "assistant",
                "Use create_task() to run coroutines concurrently.",
            ),
        ],
        start=1,
    ):
        msg = Message(
            id=None,
            conversation_id=None,
            role=role,
            content=content,
            sequence=i,
        )
        messages.append(msg)
    return messages


@pytest.fixture
def valid_json_response() -> str:
    """A valid JSON response from the LLM."""
    return (
        '{"title": "Python Async/Await Best Practices",'
        '"category": "Python",'
        '"summary": "Use asyncio with async/await for concurrency.",'
        '"content": "Python asyncio enables concurrent code.",'
        '"tags": ["python", "asyncio", "concurrency"]}'
    )


@pytest.fixture
def valid_json_with_fences() -> str:
    """Valid JSON wrapped in markdown code fences."""
    return (
        "```json\n"
        '{"title": "PostgreSQL Indexing",'
        '"category": "PostgreSQL",'
        '"summary": "B-tree indexes are the default.",'
        '"content": "B-tree indexes work well for equality queries.",'
        '"tags": ["postgresql", "indexing", "database"]}'
        "\n```"
    )


# ---------------------------------------------------------------------------
# _build_chat_text
# ---------------------------------------------------------------------------


def test_build_chat_text(sample_messages: list[Message]) -> None:
    """Test chat text construction from Message objects."""
    text = _build_chat_text(sample_messages)
    assert "user:" in text
    assert "assistant:" in text
    assert "What is the best way" in text
    assert "create_task" in text
    assert text.count("\n\n") >= 3


# ---------------------------------------------------------------------------
# _parse_json_response
# ---------------------------------------------------------------------------


def test_parse_json_response_plain(valid_json_response: str) -> None:
    """Test parsing plain JSON without fences."""
    result = _parse_json_response(valid_json_response)
    assert result["title"] == "Python Async/Await Best Practices"
    assert result["category"] == "Python"
    assert len(result["tags"]) == 3


def test_parse_json_response_with_fences(
    valid_json_with_fences: str,
) -> None:
    """Test parsing JSON wrapped in ```json fences."""
    result = _parse_json_response(valid_json_with_fences)
    assert result["title"] == "PostgreSQL Indexing"
    assert result["category"] == "PostgreSQL"


def test_parse_json_response_raises_on_invalid() -> None:
    """Test that invalid JSON raises ValueError."""
    with pytest.raises(ValueError, match="Failed to parse"):
        _parse_json_response("not valid json at all")


# ---------------------------------------------------------------------------
# _validate_extracted
# ---------------------------------------------------------------------------


def test_validate_extracted_valid(valid_json_response: str) -> None:
    """Test validation passes for valid data."""
    data = _parse_json_response(valid_json_response)
    _validate_extracted(data)


def test_validate_extracted_missing_field() -> None:
    """Test validation fails when required field is missing."""
    data = {"title": "Test", "category": "Test"}
    with pytest.raises(ValueError, match="Missing required field"):
        _validate_extracted(data)


def test_validate_extracted_empty_title() -> None:
    """Test validation fails on empty title."""
    data = {
        "title": "",
        "category": "Test",
        "summary": "Test",
        "content": "Test",
        "tags": ["test"],
    }
    with pytest.raises(ValueError, match="title"):
        _validate_extracted(data)


def test_validate_extracted_tags_not_list() -> None:
    """Test validation fails when tags is not a list."""
    data = {
        "title": "Test",
        "category": "Test",
        "summary": "Test",
        "content": "Test",
        "tags": "not a list",
    }
    with pytest.raises(ValueError, match="tags"):
        _validate_extracted(data)


# ---------------------------------------------------------------------------
# extract_knowledge (with mock LLM)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_knowledge_success(
    sample_messages: list[Message],
    valid_json_response: str,
) -> None:
    """Test full extraction pipeline with mock LLM."""
    mock_llm = MockLLMProvider(response=valid_json_response)
    result = await extract_knowledge(
        messages=sample_messages,
        llm_provider=mock_llm,
    )

    assert isinstance(result, ExtractedKnowledge)
    assert result.title == "Python Async/Await Best Practices"
    assert result.category == "Python"
    assert result.summary.startswith("Use asyncio")
    assert "asyncio" in result.content
    assert result.tags == ["python", "asyncio", "concurrency"]
    assert mock_llm.call_count == 1


@pytest.mark.asyncio
async def test_extract_knowledge_with_fences(
    sample_messages: list[Message],
    valid_json_with_fences: str,
) -> None:
    """Test extraction with markdown-fenced JSON response."""
    mock_llm = MockLLMProvider(response=valid_json_with_fences)
    result = await extract_knowledge(
        messages=sample_messages,
        llm_provider=mock_llm,
    )

    assert result.title == "PostgreSQL Indexing"
    assert result.tags == ["postgresql", "indexing", "database"]


@pytest.mark.asyncio
async def test_extract_knowledge_raises_on_invalid_json(
    sample_messages: list[Message],
) -> None:
    """Test extraction raises ValueError when LLM returns invalid JSON."""
    mock_llm = MockLLMProvider(response="this is not json")
    with pytest.raises(ValueError, match="Failed to parse"):
        await extract_knowledge(
            messages=sample_messages,
            llm_provider=mock_llm,
        )


@pytest.mark.asyncio
async def test_extract_knowledge_empty_messages() -> None:
    """Test extraction with empty message list still calls the LLM."""
    mock_llm = MockLLMProvider(
        response='{"title":"T","category":"C",'
        '"summary":"S","content":"C","tags":["t"]}'
    )
    result = await extract_knowledge(
        messages=[],
        llm_provider=mock_llm,
    )
    assert result.title == "T"
    assert result.tags == ["t"]
    assert mock_llm.call_count == 1


@pytest.mark.asyncio
async def test_extract_knowledge_prompt_contains_chat(
    sample_messages: list[Message],
    valid_json_response: str,
) -> None:
    """Test that the prompt sent to LLM contains the chat text."""
    mock_llm = MockLLMProvider(response=valid_json_response)
    await extract_knowledge(
        messages=sample_messages,
        llm_provider=mock_llm,
    )
    assert "What is the best way" in mock_llm.last_prompt
    assert "create_task" in mock_llm.last_prompt
    assert "user:" in mock_llm.last_prompt
    assert "assistant:" in mock_llm.last_prompt
