"""Request coordinator for BLUE's initial application flow."""

from collections.abc import Mapping
from typing import Any, Protocol

from contracts.messages import AssistantResponse, UserMessage
from memory.store import MemoryStore


class ReasoningEngine(Protocol):
    """Interface implemented by BLUE's reasoning component."""

    async def respond(
        self,
        message: UserMessage,
        context: Mapping[str, Any],
    ) -> AssistantResponse:
        """Generate a response without executing proposed actions."""
        ...


class Coordinator:
    """Coordinate request handling and optional persistent conversation history."""

    def __init__(
        self,
        reasoning_engine: ReasoningEngine,
        *,
        memory_store: MemoryStore | None = None,
        history_limit: int = 20,
    ) -> None:
        if (
            not isinstance(history_limit, int)
            or isinstance(history_limit, bool)
            or history_limit < 1
        ):
            raise ValueError("history_limit must be a positive integer.")

        self._reasoning_engine = reasoning_engine
        self._memory_store = memory_store
        self._history_limit = history_limit

    async def handle(self, message: UserMessage) -> AssistantResponse:
        """Handle one request and persist the exchange when storage is enabled."""

        if not isinstance(message, UserMessage):
            raise TypeError("message must be a UserMessage.")

        context: dict[str, Any] = {}

        if self._memory_store is not None:
            previous = self._memory_store.get_history(
                message.session_id,
                limit=self._history_limit,
            )

            if previous:
                context["conversation_history"] = [
                    {"role": item.role, "content": item.content}
                    for item in previous
                ]

            # Persist the user's request before calling the provider.
            self._memory_store.add_message(
                message.session_id,
                "user",
                message.text,
            )

        response = await self._reasoning_engine.respond(
            message,
            context=context,
        )

        if not isinstance(response, AssistantResponse):
            raise TypeError(
                "The reasoning engine must return an AssistantResponse."
            )

        if self._memory_store is not None:
            self._memory_store.add_message(
                message.session_id,
                "assistant",
                response.text,
            )

        # Action requests remain proposals; this coordinator does not execute them.
        return response
