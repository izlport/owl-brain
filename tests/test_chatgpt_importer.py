"""Tests for the ChatGPT import parser."""

import json
import tempfile
from pathlib import Path

import pytest

from app.importer.chatgpt.parser import parse_conversations


def _make_sample_conversations() -> list[dict]:
    """Create a minimal sample ChatGPT export JSON structure."""
    return [
        {
            "conversation_id": "conv-001",
            "title": "Test Chat about Python",
            "create_time": 1700000000.0,
            "mapping": {
                "node-1": {
                    "message": {
                        "role": "user",
                        "content": {"parts": ["Hello, how do I use Python?"]},
                        "create_time": 1700000000.0,
                    },
                },
                "node-2": {
                    "message": {
                        "role": "assistant",
                        "content": {
                            "parts": [
                                "You can start by installing Python from python.org."
                            ]
                        },
                        "create_time": 1700000010.0,
                    },
                },
                "node-3": {
                    "message": {
                        "role": "user",
                        "content": {"parts": ["Thanks! And how about virtual envs?"]},
                        "create_time": 1700000020.0,
                    },
                },
                "node-4": {
                    "message": {
                        "role": "assistant",
                        "content": {
                            "parts": [
                                "Use `python -m venv venv` to create a virtual environment."
                            ]
                        },
                        "create_time": 1700000030.0,
                    },
                },
                # A node without a message (e.g., a folder) — should be skipped
                "node-5": {
                    "message": None,
                },
                # A node with unsupported role — should be skipped
                "node-6": {
                    "message": {
                        "role": "tool",
                        "content": {"parts": ["some tool output"]},
                        "create_time": 1700000040.0,
                    },
                },
            },
        },
        {
            "conversation_id": "conv-002",
            "title": "Another conversation",
            "create_time": 1700001000.0,
            "mapping": {
                "node-10": {
                    "message": {
                        "role": "system",
                        "content": {"parts": ["You are a helpful assistant."]},
                        "create_time": 1700001000.0,
                    },
                },
            },
        },
    ]


def test_parse_conversations_basic() -> None:
    """Test basic parsing of ChatGPT export JSON."""
    sample = _make_sample_conversations()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(sample, f)
        tmp_path = f.name

    try:
        result = parse_conversations(tmp_path)

        assert len(result) == 2

        # First conversation
        conv1 = result[0]
        assert conv1.conversation_id == "conv-001"
        assert conv1.title == "Test Chat about Python"
        assert len(conv1.messages) == 4  # 2 user + 2 assistant, no tool/node-5

        # Check message ordering
        assert conv1.messages[0].role == "user"
        assert conv1.messages[0].content == "Hello, how do I use Python?"
        assert conv1.messages[1].role == "assistant"
        assert conv1.messages[2].role == "user"
        assert conv1.messages[3].role == "assistant"

        # Check sequence numbers
        assert conv1.messages[0].sequence == 1
        assert conv1.messages[3].sequence == 4

        # Second conversation
        conv2 = result[1]
        assert conv2.conversation_id == "conv-002"
        assert len(conv2.messages) == 1
        assert conv2.messages[0].role == "system"

    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_parse_conversations_empty_mapping() -> None:
    """Test conversation with empty mapping."""
    data = [
        {
            "conversation_id": "conv-empty",
            "title": "Empty",
            "create_time": 1700000000.0,
            "mapping": {},
        }
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(data, f)
        tmp_path = f.name

    try:
        result = parse_conversations(tmp_path)
        assert len(result) == 1
        assert len(result[0].messages) == 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_parse_conversations_not_a_list() -> None:
    """Test that a non-list top-level raises ValueError."""
    data = {"conversation_id": "single"}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(data, f)
        tmp_path = f.name

    try:
        with pytest.raises(ValueError, match="Expected a JSON array"):
            parse_conversations(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_parse_conversations_file_not_found() -> None:
    """Test that a missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        parse_conversations("/tmp/nonexistent_file_12345.json")
