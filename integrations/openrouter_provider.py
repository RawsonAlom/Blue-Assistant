"""OpenRouter adapter for BLUE's provider-neutral AI interface."""

from collections.abc import Mapping
from typing import Any

from openrouter import OpenRouter

from integrations.provider import (
    AIProvider,
    ModelRequest,
    ModelResponse,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


def _get_value(obj: Any, name: str, default: Any = None) -> Any:
    """Read a field from either an SDK object or a mapping."""
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


class OpenRouterProvider:
    """Generate normalized model responses through OpenRouter."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        model: str = "openrouter/free",
        client: Any | None = None,
    ) -> None:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("OpenRouter model name must not be empty.")

        if client is None:
            if not isinstance(api_key, str) or not api_key.strip():
                raise ValueError("An OpenRouter API key is required.")
            client = OpenRouter(api_key=api_key.strip())

        if not callable(
            getattr(getattr(client, "chat", None), "send_async", None)
        ):
            raise TypeError("client must provide chat.send_async().")

        self._client = client
        self._model = model.strip()

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Send one request and normalize the returned response or error."""

        if not isinstance(request, ModelRequest):
            raise TypeError("request must be a ModelRequest.")

        messages = [
            {"role": message.role, "content": message.content}
            for message in request.messages
        ]

        try:
            response = await self._client.chat.send_async(
                model=self._model,
                messages=messages,
                max_tokens=request.max_output_tokens,
                temperature=request.temperature,
                stream=False,
            )
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status is None:
                status = getattr(exc, "status", None)

            error_name = type(exc).__name__.lower()

            if status == 429:
                raise ProviderRateLimitError(
                    "OpenRouter usage limit or rate limit reached."
                ) from exc

            if (
                status in (408, 504)
                or "timeout" in error_name
                or "timeoutexception" in error_name
            ):
                raise ProviderTimeoutError(
                    "OpenRouter request timed out."
                ) from exc

            if isinstance(status, int) and status >= 500:
                raise ProviderUnavailableError(
                    "OpenRouter is temporarily unavailable."
                ) from exc

            raise ProviderError(
                "OpenRouter request failed"
                + (f" (HTTP {status})." if status is not None else ".")
            ) from exc

        choices = _get_value(response, "choices", None) or []
        if not choices:
            raise ProviderError("OpenRouter returned no response choices.")

        choice = choices[0]
        message = _get_value(choice, "message", None)
        content = _get_value(message, "content", None)

        if not isinstance(content, str) or not content.strip():
            raise ProviderError("OpenRouter returned no text content.")

        usage = _get_value(response, "usage", None)

        return ModelResponse(
            content=content.strip(),
            model=_get_value(response, "model", None) or self._model,
            finish_reason=_get_value(choice, "finish_reason", None),
            input_tokens=_get_value(usage, "prompt_tokens", None),
            output_tokens=_get_value(usage, "completion_tokens", None),
        )


# A static type check should verify that the adapter implements the
# provider-neutral protocol used by BLUE's Brain.
_PROVIDER_PROTOCOL: type[AIProvider] = OpenRouterProvider
