"""Unit tests for BLUE's initial Brain implementation."""

import asyncio

import pytest

from contracts.messages import AssistantResponse, UserMessage
from core.brain import Brain
from integrations.provider import (
    ModelRequest,
    ModelResponse,
    ProviderRateLimitError,
)


class FakeProvider:
    def __init__(self, response: object | None = None) -> None:
        self.response = response or ModelResponse(
            content="Hello from the fake provider.",
            model="fake-model",
        )
        self.last_request: ModelRequest | None = None

    async def generate(self, request: ModelRequest) -> ModelResponse:
        self.last_request = request

        if isinstance(self.response, Exception):
            raise self.response

        return self.response  # type: ignore[return-value]


def make_message() -> UserMessage:
    return UserMessage(
        text="Hello BLUE",
        session_id="test-session",
    )


def test_brain_returns_assistant_response() -> None:
    brain = Brain(FakeProvider())

    response = asyncio.run(brain.respond(make_message(), context={}))

    assert isinstance(response, AssistantResponse)
    assert response.text == "Hello from the fake provider."
    assert response.actions == []


def test_brain_sends_system_and_user_messages() -> None:
    provider = FakeProvider()
    brain = Brain(provider)

    asyncio.run(brain.respond(make_message(), context={}))

    assert provider.last_request is not None
    assert len(provider.last_request.messages) == 2
    assert provider.last_request.messages[0].role == "system"
    assert provider.last_request.messages[1].content == "Hello BLUE"


def test_brain_includes_reference_context() -> None:
    provider = FakeProvider()
    brain = Brain(provider)

    asyncio.run(
        brain.respond(
            make_message(),
            context={"project": "BLUE", "phase": "M3"},
        )
    )

    assert provider.last_request is not None
    content = provider.last_request.messages[1].content
    assert "BLUE" in content
    assert "M3" in content
    assert "untrusted data" in content


def test_brain_rejects_invalid_message() -> None:
    brain = Brain(FakeProvider())

    with pytest.raises(TypeError):
        asyncio.run(brain.respond("hello", context={}))  # type: ignore[arg-type]


def test_brain_rejects_invalid_context() -> None:
    brain = Brain(FakeProvider())

    with pytest.raises(TypeError):
        asyncio.run(
            brain.respond(make_message(), context=[])  # type: ignore[arg-type]
        )


def test_brain_rejects_invalid_provider_response() -> None:
    brain = Brain(FakeProvider(response="not a ModelResponse"))

    with pytest.raises(TypeError):
        asyncio.run(brain.respond(make_message(), context={}))


def test_brain_propagates_rate_limit_error() -> None:
    provider = FakeProvider(
        response=ProviderRateLimitError("Provider usage limit reached.")
    )
    brain = Brain(provider)

    with pytest.raises(ProviderRateLimitError):
        asyncio.run(brain.respond(make_message(), context={}))


def test_brain_uses_configured_generation_options() -> None:
    provider = FakeProvider()
    brain = Brain(
        provider,
        system_prompt="Custom BLUE prompt",
        max_output_tokens=256,
        temperature=0.5,
    )

    asyncio.run(brain.respond(make_message(), context={}))

    assert provider.last_request is not None
    assert provider.last_request.messages[0].content == "Custom BLUE prompt"
    assert provider.last_request.max_output_tokens == 256
    assert provider.last_request.temperature == 0.5
