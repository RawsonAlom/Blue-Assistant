"""Tests for BLUE's provider-neutral AI interfaces."""

import asyncio

import pytest

from integrations.provider import (
    AIProvider,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ProviderError,
    ProviderRateLimitError,
)


def test_model_request_accepts_valid_messages() -> None:
    request = ModelRequest(
        messages=(
            ModelMessage(role="system", content="You are BLUE."),
            ModelMessage(role="user", content="Hello."),
        )
    )

    assert len(request.messages) == 2
    assert request.max_output_tokens == 512


def test_model_message_rejects_empty_content() -> None:
    with pytest.raises(ValueError):
        ModelMessage(role="user", content="  ")


def test_model_request_rejects_empty_messages() -> None:
    with pytest.raises(ValueError):
        ModelRequest(messages=())


def test_model_request_rejects_invalid_token_limit() -> None:
    with pytest.raises(ValueError):
        ModelRequest(
            messages=(ModelMessage(role="user", content="Hi"),),
            max_output_tokens=0,
        )


def test_model_request_rejects_invalid_temperature() -> None:
    with pytest.raises(ValueError):
        ModelRequest(
            messages=(ModelMessage(role="user", content="Hi"),),
            temperature=3.0,
        )


def test_model_response_rejects_negative_usage() -> None:
    with pytest.raises(ValueError):
        ModelResponse(
            content="Hello",
            model="test-model",
            input_tokens=-1,
        )


def test_provider_errors_share_common_base() -> None:
    error = ProviderRateLimitError("Usage limit reached.")

    assert isinstance(error, ProviderError)


def test_fake_provider_implements_contract() -> None:
    class FakeProvider:
        async def generate(self, request: ModelRequest) -> ModelResponse:
            assert request.messages[-1].content == "Hello"
            return ModelResponse(
                content="Hello from a fake provider.",
                model="fake-model",
                input_tokens=1,
                output_tokens=5,
            )

    provider: AIProvider = FakeProvider()
    request = ModelRequest(
        messages=(ModelMessage(role="user", content="Hello"),)
    )

    response = asyncio.run(provider.generate(request))

    assert response.model == "fake-model"
    assert response.content == "Hello from a fake provider."
