"""Initial request coordinator with an injectable reasoning interface."""

from collections.abc import Mapping
from typing import Any, Protocol

from contracts.messages import AssistantResponse, UserMessage


class ReasoningEngine(Protocol):
    """Interface implemented by a future Brain or provider adapter."""

    async def respond(
        self,
        message: UserMessage,
        context: Mapping[str, Any],
    ) -> AssistantResponse:
        """Produce a response without executing proposed actions."""
        ...


class Coordinator:
    """Pass a validated user request to the configured reasoning engine."""

    def __init__(self, reasoning_engine: ReasoningEngine) -> None:
        self._reasoning_engine = reasoning_engine

    async def handle(self, message: UserMessage) -> AssistantResponse:
        """Handle one request using the initial empty-context interface."""

        if not isinstance(message, UserMessage):
            raise TypeError("message must be a UserMessage.")

        response = await self._reasoning_engine.respond(
            message,
            context={},
        )

        if not isinstance(response, AssistantResponse):
            raise TypeError(
                "The reasoning engine must return an AssistantResponse."
            )

        # Action requests remain proposals. Execution and authorization
        # will be implemented in a later milestone.
        return response
