"""Offline tests for BLUE's terminal text chat."""

import asyncio

from contracts.messages import AssistantResponse, UserMessage
from integrations.provider import (
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from main import run_chat
from memory.store import MemoryStore


class FakeBrain:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.messages: list[UserMessage] = []

    async def respond(
        self,
        message: UserMessage,
        context: dict[str, object],
    ) -> AssistantResponse:
        self.messages.append(message)

        if self.error is not None:
            raise self.error

        assert context == {}
        return AssistantResponse(text=f"Echo: {message.text}")


def make_input(answers: list[str]):
    remaining = iter(answers)

    def get_input(_prompt: str) -> str:
        return next(remaining)

    return get_input


def test_text_chat_sends_message_to_brain() -> None:
    brain = FakeBrain()
    output: list[str] = []

    asyncio.run(
        run_chat(
            brain,
            input_fn=make_input(["Hello BLUE", "exit"]),
            output_fn=output.append,
        )
    )

    assert len(brain.messages) == 1
    assert brain.messages[0].text == "Hello BLUE"
    assert brain.messages[0].source == "text"
    assert "BLUE: Echo: Hello BLUE" in output


def test_text_chat_ignores_blank_input() -> None:
    brain = FakeBrain()
    output: list[str] = []

    asyncio.run(
        run_chat(
            brain,
            input_fn=make_input(["   ", "exit"]),
            output_fn=output.append,
        )
    )

    assert brain.messages == []
    assert "BLUE: Goodbye." in output


def test_text_chat_handles_rate_limit() -> None:
    brain = FakeBrain(
        error=ProviderRateLimitError("private provider details")
    )
    output: list[str] = []

    asyncio.run(
        run_chat(
            brain,
            input_fn=make_input(["Hello", "exit"]),
            output_fn=output.append,
        )
    )

    assert any("usage limit reached" in line for line in output)
    assert all("private provider details" not in line for line in output)


def test_text_chat_handles_provider_unavailable() -> None:
    brain = FakeBrain(error=ProviderUnavailableError("temporary outage"))
    output: list[str] = []

    asyncio.run(
        run_chat(
            brain,
            input_fn=make_input(["Hello", "exit"]),
            output_fn=output.append,
        )
    )

    assert any("temporarily unavailable" in line for line in output)
    assert len(brain.messages) == 1


def test_text_chat_handles_end_of_input() -> None:
    brain = FakeBrain()
    output: list[str] = []

    def no_more_input(_prompt: str) -> str:
        raise EOFError

    asyncio.run(
        run_chat(brain, input_fn=no_more_input, output_fn=output.append)
    )

    assert brain.messages == []
    assert any("BLUE: Session ended." in line for line in output)


def test_text_chat_persists_conversation(tmp_path) -> None:
    store = MemoryStore(tmp_path / "chat-history.sqlite3")
    brain = FakeBrain()
    output: list[str] = []

    asyncio.run(
        run_chat(
            brain,
            input_fn=make_input(["Hello BLUE", "exit"]),
            output_fn=output.append,
            memory_store=store,
        )
    )

    history = store.get_history("terminal-session")

    assert [(item.role, item.content) for item in history] == [
        ("user", "Hello BLUE"),
        ("assistant", "Echo: Hello BLUE"),
    ]
