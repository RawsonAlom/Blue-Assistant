"""Unit tests for BLUE's initial contracts and coordinator."""

import asyncio

import pytest

from contracts.messages import (
    ActionRequest,
    ActionResult,
    AssistantResponse,
    UserMessage,
)
from core.config import Settings
from core.coordinator import Coordinator
from memory.store import MemoryStore


def test_user_message_accepts_text_request() -> None:
    message = UserMessage(
        text="Hello BLUE",
        session_id="test-session",
    )

    assert message.text == "Hello BLUE"
    assert message.source == "text"


def test_user_message_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        UserMessage(text="   ", session_id="test-session")


def test_action_request_rejects_unknown_risk_level() -> None:
    with pytest.raises(ValueError):
        ActionRequest(name="light_on", risk_level="extreme")  # type: ignore[arg-type]


def test_assistant_response_requires_action_requests() -> None:
    with pytest.raises(TypeError):
        AssistantResponse(
            text="Proposed action",
            actions=["light_on"],  # type: ignore[list-item]
        )


def test_action_result_rejects_unknown_status() -> None:
    with pytest.raises(ValueError):
        ActionResult(
            action_name="light_on",
            status="maybe",  # type: ignore[arg-type]
            message="Not verified",
        )


def test_settings_load_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLUE_APP_NAME", "BLUE Test")
    monkeypatch.setenv("BLUE_ENV", "test")
    monkeypatch.setenv("BLUE_LOG_LEVEL", "DEBUG")

    settings = Settings.from_environment()

    assert settings.app_name == "BLUE Test"
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"


def test_coordinator_passes_request_to_reasoning_engine() -> None:
    message = UserMessage(
        text="Hello BLUE",
        session_id="test-session",
    )
    expected = AssistantResponse(text="Hello from a fake brain.")

    class FakeBrain:
        async def respond(
            self,
            incoming: UserMessage,
            context: dict[str, object],
        ) -> AssistantResponse:
            assert incoming is message
            assert context == {}
            return expected

    coordinator = Coordinator(FakeBrain())
    actual = asyncio.run(coordinator.handle(message))

    assert actual is expected


def test_coordinator_rejects_invalid_message() -> None:
    class FakeBrain:
        async def respond(
            self,
            message: UserMessage,
            context: dict[str, object],
        ) -> AssistantResponse:
            return AssistantResponse(text="Unused")

    with pytest.raises(TypeError):
        asyncio.run(Coordinator(FakeBrain()).handle("not a message"))  # type: ignore[arg-type]



def test_coordinator_persists_conversation(tmp_path) -> None:
    store = MemoryStore(tmp_path / "conversation.sqlite3")
    message = UserMessage(
        text="Hello BLUE",
        session_id="session-1",
    )
    expected = AssistantResponse(text="Hello from BLUE.")

    class FakeBrain:
        async def respond(
            self,
            incoming: UserMessage,
            context: dict[str, object],
        ) -> AssistantResponse:
            assert incoming is message
            assert context == {}
            return expected

    response = asyncio.run(
        Coordinator(FakeBrain(), memory_store=store).handle(message)
    )

    history = store.get_history("session-1")

    assert response is expected
    assert [(item.role, item.content) for item in history] == [
        ("user", "Hello BLUE"),
        ("assistant", "Hello from BLUE."),
    ]


def test_coordinator_provides_previous_history(tmp_path) -> None:
    store = MemoryStore(tmp_path / "history.sqlite3")
    store.add_message("session-2", "user", "My favourite colour is blue.")
    store.add_message("session-2", "assistant", "I understand.")

    message = UserMessage(
        text="What colour did I mention?",
        session_id="session-2",
    )

    class HistoryAwareBrain:
        def __init__(self) -> None:
            self.received_context: dict[str, object] = {}

        async def respond(
            self,
            incoming: UserMessage,
            context: dict[str, object],
        ) -> AssistantResponse:
            self.received_context = context
            return AssistantResponse(text="Blue.")

    brain = HistoryAwareBrain()

    asyncio.run(
        Coordinator(brain, memory_store=store).handle(message)
    )

    history = brain.received_context["conversation_history"]

    assert history == [
        {"role": "user", "content": "My favourite colour is blue."},
        {"role": "assistant", "content": "I understand."},
    ]


def test_coordinator_can_run_without_memory_store() -> None:
    message = UserMessage(text="Hello", session_id="no-memory-session")
    expected = AssistantResponse(text="Hello.")

    class FakeBrain:
        async def respond(
            self,
            incoming: UserMessage,
            context: dict[str, object],
        ) -> AssistantResponse:
            assert context == {}
            return expected

    result = asyncio.run(Coordinator(FakeBrain()).handle(message))
    assert result is expected


def test_coordinator_rejects_invalid_history_limit() -> None:
    class FakeBrain:
        async def respond(
            self,
            message: UserMessage,
            context: dict[str, object],
        ) -> AssistantResponse:
            return AssistantResponse(text="Unused.")

    with pytest.raises(ValueError):
        Coordinator(FakeBrain(), history_limit=0)
