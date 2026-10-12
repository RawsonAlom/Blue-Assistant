"""Shared, provider-neutral message contracts for BLUE."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

MessageSource = Literal["text", "voice"]
RiskLevel = Literal["low", "medium", "high"]
ActionStatus = Literal["success", "failure", "denied", "unknown"]

_VALID_SOURCES = {"text", "voice"}
_VALID_RISK_LEVELS = {"low", "medium", "high"}
_VALID_ACTION_STATUSES = {"success", "failure", "denied", "unknown"}


@dataclass(frozen=True, slots=True)
class UserMessage:
    """A normalized user request, independent of its input interface."""

    text: str
    session_id: str
    source: MessageSource = "text"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("UserMessage.text must not be empty.")

        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("UserMessage.session_id must not be empty.")

        if self.source not in _VALID_SOURCES:
            raise ValueError(f"Unsupported message source: {self.source!r}")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("UserMessage.metadata must be a mapping.")


@dataclass(frozen=True, slots=True)
class ActionRequest:
    """A proposed operation; it is not authorization to execute it."""

    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    reason: str | None = None
    risk_level: RiskLevel | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("ActionRequest.name must not be empty.")

        if not isinstance(self.arguments, Mapping):
            raise TypeError("ActionRequest.arguments must be a mapping.")

        if (
            self.risk_level is not None
            and self.risk_level not in _VALID_RISK_LEVELS
        ):
            raise ValueError(
                f"Unsupported risk level: {self.risk_level!r}"
            )


@dataclass(frozen=True, slots=True)
class AssistantResponse:
    """A normalized assistant response with optional proposed actions."""

    text: str
    actions: list[ActionRequest] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("AssistantResponse.text must not be empty.")

        if not isinstance(self.actions, list):
            raise TypeError("AssistantResponse.actions must be a list.")

        if not all(isinstance(action, ActionRequest) for action in self.actions):
            raise TypeError(
                "Every AssistantResponse action must be an ActionRequest."
            )


@dataclass(frozen=True, slots=True)
class ActionResult:
    """The reported outcome of an attempted action."""

    action_name: str
    status: ActionStatus
    message: str
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.action_name, str) or not self.action_name.strip():
            raise ValueError("ActionResult.action_name must not be empty.")

        if self.status not in _VALID_ACTION_STATUSES:
            raise ValueError(f"Unsupported action status: {self.status!r}")

        if not isinstance(self.message, str):
            raise TypeError("ActionResult.message must be a string.")

        if not isinstance(self.data, Mapping):
            raise TypeError("ActionResult.data must be a mapping.")
