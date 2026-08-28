from agentsite.capabilities import Capability, CapabilityRegistry
from agentsite.models import AgentRequest, ModelTurn, ToolCall
from agentsite.provider import ScriptedProvider
from agentsite.runtime import AgentRuntime


def registry():
    calls = []
    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="customers.lookup",
            description="Look up a customer by email.",
            input_schema={
                "type": "object",
                "properties": {"email": {"type": "string"}},
                "required": ["email"],
            },
            execute=lambda args, context: calls.append((args, context)) or {"name": "Ayan"},
        )
    )
    registry.register(
        Capability(
            name="orders.create",
            description="Create an order.",
            input_schema={"type": "object", "properties": {"sku": {"type": "string"}}, "required": ["sku"]},
            execute=lambda args, context: {"order_id": "ord_123"},
            risk="consequential",
            requires_approval=True,
        )
    )
    return registry, calls


def test_read_capability_is_executed_server_side():
    registry, calls = registry()
    provider = ScriptedProvider(
        [
            ModelTurn(tool_calls=(ToolCall("c1", "customers.lookup", {"email": "ayan@example.com"}),)),
            ModelTurn(assistant_text="The customer is Ayan."),
        ]
    )
    response = AgentRuntime(provider, registry).handle(AgentRequest("Find Ayan", "u1", "t1"))
    assert response.text == "The customer is Ayan."
    assert calls == [({"email": "ayan@example.com"}, {"user_id": "u1", "tenant_id": "t1"})]
    assert response.results[0].status == "completed"


def test_consequential_capability_stops_for_approval():
    registry, _ = registry()
    response = AgentRuntime(
        ScriptedProvider([ModelTurn(tool_calls=(ToolCall("c2", "orders.create", {"sku": "book"}),))]), registry
    ).handle(AgentRequest("Buy a book", "u1", "t1"))
    assert response.pending_approvals[0].call_id == "c2"
    assert response.results[0].status == "approval_required"


def test_invalid_arguments_never_reach_adapter():
    registry, calls = registry()
    response = AgentRuntime(
        ScriptedProvider([ModelTurn(tool_calls=(ToolCall("c3", "customers.lookup", {"email": 42}),))]), registry
    ).handle(AgentRequest("Find customer", "u1", "t1"))
    assert response.results[0].status == "failed"
    assert calls == []
