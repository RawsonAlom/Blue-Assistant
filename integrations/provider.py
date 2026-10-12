"""Provider-neutral interfaces for BLUE's AI model integrations."""

from dataclasses import dataclass
from typing import Literal, Protocol

MessageRole = Literal["system", "user", "assistant"]
_ALLOWED_ROLES = {"system", "user", "assistant"}


@dataclass(frozen=True, slots=True)
class ModelMessage:
    """One normalized message sent to an AI model."""

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if self.role not in _ALLOWED_ROLES:
            raise ValueError(f"Unsupported message role: {self.role!r}")

        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Message content must not be empty.")


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """A provider-independent model generation request."""

    messages: tuple[ModelMessage, ...]
    max_output_tokens: int = 512
    temperature: float = 0.2

    def __post_init__(self) -> None:
        if not isinstance(self.messages, tuple) or not self.messages:
            raise ValueError("Messages must be a non-empty tuple.")

        if not all(
            isinstance(message, ModelMessage)
            for message in self.messages
        ):
            raise TypeError("Every message must be a ModelMessage.")

        if (
            not isinstance(self.max_output_tokens, int)
            or isinstance(self.max_output_tokens, bool)
            or self.max_output_tokens <= 0
        ):
            raise ValueError("max_output_tokens must be a positive integer.")

        if (
            not isinstance(self.temperature, (int, float))
            or isinstance(self.temperature, bool)
            or not 0.0 <= self.temperature <= 2.0
        ):
            raise ValueError("temperature must be between 0.0 and 2.0.")


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """Normalized output returned by an AI provider."""

    content: str
    model: str
    finish_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Response content must not be empty.")

        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("Model name must not be empty.")

        for name, value in (
            ("input_tokens", self.input_tokens),
            ("output_tokens", self.output_tokens),
        ):
            if value is not None and (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(f"{name} must be a non-negative integer.")


class ProviderError(RuntimeError):
    """Base exception for normalized provider failures."""


class ProviderRateLimitError(ProviderError):
    """The provider rejected a request because of a usage limit."""


class ProviderTimeoutError(ProviderError):
    """The provider request timed out."""


class ProviderUnavailableError(ProviderError):
    """The provider could not process the request."""


class AIProvider(Protocol):
    """Interface that every runtime AI provider adapter must implement."""

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response without executing application actions."""
        ...
