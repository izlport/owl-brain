"""CLI entry point for importing ChatGPT conversations.

Usage:
    uv run python -m app.importer.chatgpt.cli --file conversations.json
"""

import argparse
import asyncio
import logging
import sys

from app.importer.chatgpt.importer import import_conversations


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Import ChatGPT export conversations.json into Owl Brain.",
    )
    parser.add_argument(
        "--file",
        required=True,
        type=str,
        help="Path to ChatGPT export conversations.json file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug-level logging",
    )
    return parser.parse_args(argv)


async def main_async(args: argparse.Namespace) -> None:
    """Async main logic."""
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("Owl Brain - ChatGPT Import Tool")
    logger.info("File: %s", args.file)

    result = await import_conversations(file_path=args.file)

    logger.info(
        "Result: %d conversations, %d messages imported successfully",
        result["conversations"],
        result["messages"],
    )


def main() -> None:
    """Sync entry point."""
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
