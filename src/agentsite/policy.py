from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .capabilities import Capability
from .models import AgentRequest, ToolCall


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    approval_required: bool = False
    reason: str | None = None


class PolicyEngine:
    """Default deny for unknown actions; customize for tenant/role policy."""

    def decide(self, request: AgentRequest, call: ToolCall, capability: Capability) -> PolicyDecision:
        if capability.requires_approval and call.call_id not in request.approved_invocations:
            return PolicyDecision(False, approval_required=True, reason="explicit approval required")
        return PolicyDecision(True)

    def context(self, request: AgentRequest) -> dict[str, Any]:
        return {"user_id": request.user_id, "tenant_id": request.tenant_id}
