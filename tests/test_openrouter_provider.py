"""Offline tests for BLUE's OpenRouter provider adapter."""

import asyncio
from types import SimpleNamespace

import pytest

from integrations.openrouter_provider import OpenRouterProvider
from integrations.provider import (
    ModelMessage,
    ModelRequest,
    ProviderError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


class FakeAPIError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__("fake provider error")
        self.status_code = status_code


class FakeChat:
    def __init__(self, response=None, error=None) -> None:
        self.response = response or SimpleNamespace(
            model="fake/provider",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Hello from fake OpenRouter."),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=12,
                completion_tokens=7,
            ),
        )
        self.error = error
        self.last_request = None

    async def send_async(self, **kwargs):
        self.last_request = kwargs
        if self.error is not None:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, chat: FakeChat) -> None:
        self.chat = chat


def make_request() -> ModelRequest:
    return ModelRequest(
        messages=(
            ModelMessage(role="system", content="You are BLUE."),
            ModelMessage(role="user", content="Hello."),
        ),
        max_output_tokens=128,
        temperature=0.2,
    )


def make_provider(chat: FakeChat | None = None) -> OpenRouterProvider:
    return OpenRouterProvider(
        client=FakeClient(chat or FakeChat()),
    )


def test_provider_normalizes_response() -> None:
    provider = make_provider()

    response = asyncio.run(provider.generate(make_request()))

    assert response.content == "Hello from fake OpenRouter."
    assert response.model == "fake/provider"
    assert response.finish_reason == "stop"
    assert response.input_tokens == 12
    assert response.output_tokens == 7


def test_provider_sends_expected_request() -> None:
    chat = FakeChat()
    provider = make_provider(chat)

    asyncio.run(provider.generate(make_request()))

    assert chat.last_request is not None
    assert chat.last_request["model"] == "openrouter/free"
    assert chat.last_request["messages"][0]["role"] == "system"
    assert chat.last_request["messages"][1]["content"] == "Hello."
    assert chat.last_request["max_tokens"] == 128
    assert chat.last_request["stream"] is False


def test_provider_accepts_configured_model() -> None:
    provider = OpenRouterProvider(
        model="example/test-model",
        client=FakeClient(FakeChat()),
    )

    response = asyncio.run(provider.generate(make_request()))

    assert response.content == "Hello from fake OpenRouter."


def test_provider_requires_api_key_without_client() -> None:
    with pytest.raises(ValueError, match="API key"):
        OpenRouterProvider(api_key="")


def test_provider_maps_rate_limit() -> None:
    provider = make_provider(FakeChat(error=FakeAPIError(429)))

    with pytest.raises(ProviderRateLimitError):
        asyncio.run(provider.generate(make_request()))


def test_provider_maps_service_unavailable() -> None:
    provider = make_provider(FakeChat(error=FakeAPIError(503)))

    with pytest.raises(ProviderUnavailableError):
        asyncio.run(provider.generate(make_request()))


def test_provider_rejects_missing_response_text() -> None:
    chat = FakeChat(
        response=SimpleNamespace(
            model="fake/provider",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=None),
                    finish_reason="stop",
                )
            ],
            usage=None,
        )
    )
    provider = make_provider(chat)

    with pytest.raises(ProviderError, match="no text content"):
        asyncio.run(provider.generate(make_request()))
