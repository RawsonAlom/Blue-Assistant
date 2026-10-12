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
