from __future__ import annotations

from typing import Any, Protocol, Sequence

from .models import Message, ModelTurn


class ModelProvider(Protocol):
    def complete(self, messages: Sequence[Message], capabilities: list[dict[str, Any]]) -> ModelTurn:
        """Return either a final answer or typed capability calls."""


class ScriptedProvider:
    """Tiny deterministic provider used by tests and local development.

    A production provider adapter can translate this same contract to any LLM API.
    """

    def __init__(self, turns: list[ModelTurn]) -> None:
        self._turns = iter(turns)

    def complete(self, messages: Sequence[Message], capabilities: list[dict[str, Any]]) -> ModelTurn:
        return next(self._turns)
