"""Terminal text-chat entry point for BLUE."""

import asyncio
import sys
from collections.abc import Callable

from contracts.messages import UserMessage
from core.brain import Brain
from core.runtime import create_brain
from integrations.provider import (
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


async def run_chat(
    brain: Brain,
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> None:
    """Run a text conversation with injectable input and output."""

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
            response = await brain.respond(message, context={})
        except ProviderRateLimitError:
            output_fn(
                "BLUE: Provider usage limit reached. "
                "Check availability before trying again."
            )
        except ProviderTimeoutError:
            output_fn("BLUE: The AI request timed out.")
        except ProviderUnavailableError:
            output_fn(
                "BLUE: The AI service is temporarily unavailable. "
                "No action was executed."
            )
        except ProviderError:
            output_fn(
                "BLUE: The AI request failed. Check configuration "
                "and try again later."
            )
        else:
            output_fn(f"BLUE: {response.text}")


def main() -> int:
    """Create the configured Brain and start the chat."""

    try:
        brain = create_brain()
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    try:
        asyncio.run(run_chat(brain))
    except KeyboardInterrupt:
        print("\nBLUE: Session ended.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
