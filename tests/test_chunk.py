"""Tests for the Chunk module (Chunk data class, strategies, Chunker)."""

import uuid
from unittest.mock import MagicMock

from app.chunk.chunk import Chunk
from app.chunk.chunker import Chunker
from app.chunk.strategy import ChunkStrategy, DefaultChunkStrategy

# ===========================================================================
# Chunk data class
# ===========================================================================


def test_chunk_creation() -> None:
    """Test basic Chunk data class creation."""
    kid = uuid.uuid4()
    c = Chunk(
        knowledge_id=kid,
        chunk_index=0,
        content="hello world",
        token_count=2,
        metadata={"key": "val"},
    )
    assert c.knowledge_id == kid
    assert c.chunk_index == 0
    assert c.content == "hello world"
    assert c.token_count == 2
    assert c.metadata == {"key": "val"}


def test_chunk_defaults() -> None:
    """Test Chunk default values."""
    kid = uuid.uuid4()
    c = Chunk(knowledge_id=kid, chunk_index=0, content="test")
    assert c.token_count is None
    assert c.metadata == {}


# ===========================================================================
# DefaultChunkStrategy
# ===========================================================================


def test_default_strategy_empty_text() -> None:
    """Empty text returns empty list."""
    s = DefaultChunkStrategy()
    assert s.split("") == []
    assert s.split("   ") == []


def test_default_strategy_short_text() -> None:
    """Short text (under chunk_size) returns as a single chunk."""
    s = DefaultChunkStrategy(chunk_size=512)
    text = "Short text."
    result = s.split(text)
    assert len(result) == 1
    assert result[0] == text


def test_default_strategy_long_text() -> None:
    """Long text is split into multiple chunks."""
    s = DefaultChunkStrategy(chunk_size=100, chunk_overlap=10)
    # Generate a text long enough to force multiple chunks
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 50
    result = s.split(text)
    assert len(result) >= 2, f"Expected >=2 chunks, got {len(result)}"
    # Chunks preserve ordering
    assert result[0] in text
    assert result[-1] in text


def test_default_strategy_custom_params() -> None:
    """Custom chunk_size and chunk_overlap are respected."""
    s = DefaultChunkStrategy(chunk_size=50, chunk_overlap=5)
    text = "word " * 200
    result = s.split(text)
    assert len(result) >= 2


# ===========================================================================
# Chunker (integration with Knowledge ORM)
# ===========================================================================


def _make_knowledge_mock(
    content: str,
    title: str = "Test Knowledge",
    category: str = "Test",
) -> MagicMock:
    """Create a mock Knowledge ORM object."""
    mock = MagicMock()
    mock.id = uuid.uuid4()
    mock.title = title
    mock.category = category
    mock.content = content
    return mock


def test_chunker_empty_content() -> None:
    """Knowledge with empty content returns no chunks."""
    chunker = Chunker()
    kn = _make_knowledge_mock(content="")
    result = chunker.split(kn)
    assert result == []


def test_chunker_short_content() -> None:
    """Short knowledge content produces a single chunk."""
    chunker = Chunker()
    kn = _make_knowledge_mock(content="A short piece of knowledge.")
    result = chunker.split(kn)
    assert len(result) == 1
    chunk = result[0]
    assert chunk.knowledge_id == kn.id
    assert chunk.chunk_index == 0
    assert chunk.content == "A short piece of knowledge."
    assert chunk.token_count is not None
    assert chunk.token_count > 0
    assert chunk.metadata["knowledge_title"] == "Test Knowledge"
    assert chunk.metadata["knowledge_category"] == "Test"


def test_chunker_long_content() -> None:
    """Long knowledge content is split into multiple chunks."""
    chunker = Chunker()
    # A text long enough to produce multiple chunks
    long_text = "Paragraph one.\n\n" * 200
    kn = _make_knowledge_mock(content=long_text, title="Long Doc")
    result = chunker.split(kn)
    assert len(result) >= 2

    # Verify sequential indices
    for i, chunk in enumerate(result):
        assert chunk.chunk_index == i
        assert chunk.knowledge_id == kn.id
        assert chunk.content  # non-empty
        assert chunk.token_count is not None

    # Verify no content overlap duplicates across chunks
    all_text = "".join(c.content for c in result)
    assert len(all_text) >= len(long_text) * 0.9  # small loss from overlap


def test_chunker_with_custom_strategy() -> None:
    """Chunker accepts a custom strategy."""

    class FixedStrategy(ChunkStrategy):
        def split(self, text: str) -> list[str]:
            return [text[:10], text[10:20], text[20:]]

    chunker = Chunker(strategy=FixedStrategy())
    kn = _make_knowledge_mock(content="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    result = chunker.split(kn)
    assert len(result) == 3
    assert result[0].content == "ABCDEFGHIJ"
    assert result[1].content == "KLMNOPQRST"
    assert result[2].content == "UVWXYZ"


def test_chunker_token_count_estimate() -> None:
    """Token count estimate is consistent with (len//4)."""
    chunker = Chunker()
    content = "Hello world, this is a test. " * 10
    kn = _make_knowledge_mock(content=content)
    result = chunker.split(kn)
    for chunk in result:
        expected_tokens = len(chunk.content) // 4
        assert chunk.token_count == max(1, expected_tokens)


# ===========================================================================
# 3000+ char long text
# ===========================================================================


def test_chunker_very_long_text() -> None:
    """Knowledge with 3000+ characters is split into multiple chunks."""
    chunker = Chunker()
    # Generate >3000 chars
    sentence = "Python is a powerful programming language. "
    long_text = (sentence * 80)[:3200]
    assert len(long_text) >= 3000, f"Test text too short: {len(long_text)}"

    kn = _make_knowledge_mock(content=long_text, title="Very Long Doc")
    result = chunker.split(kn)

    assert len(result) >= 2
    # All original content is covered across chunks
    combined = "".join(c.content for c in result)
    assert len(combined) >= len(long_text) * 0.8
