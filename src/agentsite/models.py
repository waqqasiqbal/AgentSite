from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Role = Literal["user", "assistant", "tool"]


@dataclass(frozen=True)
class AgentRequest:
    text: str
    user_id: str
    tenant_id: str
    approved_invocations: frozenset[str] = frozenset()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    capability: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    capability: str
    status: Literal["completed", "failed", "denied", "approval_required"]
    output: Any = None
    error: str | None = None


@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    tool_call_id: str | None = None


@dataclass(frozen=True)
class ModelTurn:
    assistant_text: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()


@dataclass(frozen=True)
class AgentResponse:
    text: str
    trace_id: str
    results: tuple[ToolResult, ...] = ()
    pending_approvals: tuple[ToolCall, ...] = ()
    messages: tuple[Message, ...] = ()
