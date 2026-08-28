from __future__ import annotations

import uuid
from dataclasses import replace

from .capabilities import CapabilityRegistry, CapabilityError
from .models import AgentRequest, AgentResponse, Message, ModelTurn, ToolCall, ToolResult
from .policy import PolicyEngine
from .provider import ModelProvider


class AgentRuntime:
    def __init__(
        self,
        provider: ModelProvider,
        capabilities: CapabilityRegistry,
        policy: PolicyEngine | None = None,
        max_turns: int = 8,
    ) -> None:
        self.provider = provider
        self.capabilities = capabilities
        self.policy = policy or PolicyEngine()
        self.max_turns = max_turns

    def handle(self, request: AgentRequest) -> AgentResponse:
        trace_id = uuid.uuid4().hex
        messages = [Message("user", request.text)]
        results: list[ToolResult] = []
        pending: list[ToolCall] = []

        for _ in range(self.max_turns):
            turn = self.provider.complete(messages, self.capabilities.definitions())
            if turn.assistant_text is not None and not turn.tool_calls:
                return AgentResponse(turn.assistant_text, trace_id, tuple(results), tuple(pending), tuple(messages))

            for call in turn.tool_calls:
                capability = self.capabilities.get(call.capability)
                if capability is None:
                    result = ToolResult(call.call_id, call.capability, "denied", error="unknown capability")
                else:
                    try:
                        capability.validate(call.arguments)
                        decision = self.policy.decide(request, call, capability)
                        if decision.approval_required:
                            pending.append(call)
                            result = ToolResult(call.call_id, call.capability, "approval_required", error=decision.reason)
                        elif not decision.allowed:
                            result = ToolResult(call.call_id, call.capability, "denied", error=decision.reason)
                        else:
                            try:
                                output = capability.execute(call.arguments, self.policy.context(request))
                                result = ToolResult(call.call_id, call.capability, "completed", output=output)
                            except Exception as exc:  # adapter failures become model-visible tool errors
                                result = ToolResult(call.call_id, call.capability, "failed", error=str(exc))
                    except CapabilityError as exc:
                        result = ToolResult(call.call_id, call.capability, "failed", error=str(exc))

                results.append(result)
                messages.append(Message("tool", _serialize_result(result), call.call_id))

            if pending:
                return AgentResponse(
                    "Approval is required before I can continue.", trace_id, tuple(results), tuple(pending), tuple(messages)
                )

        return AgentResponse("The request could not be completed within the execution limit.", trace_id, tuple(results), tuple(pending), tuple(messages))


def _serialize_result(result: ToolResult) -> str:
    if result.status == "completed":
        return f"completed: {result.output!r}"
    return f"{result.status}: {result.error or 'no further details'}"
