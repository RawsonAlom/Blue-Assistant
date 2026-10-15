"""Terminal text-chat entry point for BLUE."""

import asyncio
import os
import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

from contracts.messages import UserMessage
from core.brain import Brain
from core.coordinator import Coordinator
from core.runtime import create_brain
from integrations.provider import (
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from memory.store import MemoryStore

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


def default_memory_path() -> Path:
    """Return a persistent database path outside the project repository."""

    configured_home = os.environ.get("XDG_DATA_HOME")
    data_home = (
        Path(configured_home).expanduser()
        if configured_home
        else Path.home() / ".local" / "share"
    )
    return data_home / "blue" / "blue.sqlite3"


async def run_chat(
    brain: Brain,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
    memory_store: MemoryStore | None = None,
) -> None:
    """Run terminal chat with optional persistent conversation history."""

    coordinator = Coordinator(brain, memory_store=memory_store)
    session_id = "terminal-session"

    output_fn("BLUE text chat. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            text = input_fn("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\nBLUE: Session ended.")
            return

        if not text:
            continue

        if text.lower() in {"exit", "quit"}:
            output_fn("BLUE: Goodbye.")
            return

        message = UserMessage(
            text=text,
            session_id=session_id,
            source="text",
        )

        try:
            response = await coordinator.handle(message)
        except ProviderRateLimitError:
            output_fn("BLUE: Provider usage limit reached.")
        except ProviderTimeoutError:
            output_fn("BLUE: The AI request timed out.")
        except ProviderUnavailableError:
            output_fn("BLUE: The AI service is temporarily unavailable.")
        except ProviderError:
            output_fn("BLUE: The AI request failed. Check configuration.")
        else:
            output_fn(f"BLUE: {response.text}")


def main() -> int:
    """Create the configured Brain and start the text chat."""

    try:
        brain = create_brain()
        memory_store = MemoryStore(default_memory_path())
    except (RuntimeError, OSError, sqlite3.Error) as exc:
        print(f"Startup error: {exc}", file=sys.stderr)
        return 2

    try:
        asyncio.run(run_chat(brain, memory_store=memory_store))
    except KeyboardInterrupt:
        print("\nBLUE: Session ended.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
