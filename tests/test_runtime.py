from agentsite.capabilities import Capability, CapabilityRegistry
from agentsite.models import AgentRequest, ModelTurn, ToolCall
from agentsite.provider import ScriptedProvider
from agentsite.runtime import AgentRuntime
from agentsite.manifest import AgentManifest
from examples.business_capabilities import build_reference_registry


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


def test_manifest_is_machine_readable():
    manifest = AgentManifest.from_dict(
        {"name": "demo", "display_name": "Demo", "description": "A demo", "capabilities": ["customers.lookup"]}
    )
    assert manifest.to_dict()["capabilities"] == ["customers.lookup"]


def test_ecommerce_search_returns_current_product_details():
    registry = build_reference_registry()
    capability = registry.get("catalog.search_products")
    result = capability.execute({"query": "headphones", "limit": 5}, {"tenant_id": "shop-1"})
    assert result[0]["price"] == 129.0
    assert result[0]["currency"] == "EUR"


def test_insurance_quote_is_explicitly_non_binding():
    registry = build_reference_registry()
    capability = registry.get("insurance.create_quote")
    result = capability.execute(
        {"insurance_product": "travel", "customer_details": {"destination": "Spain"}},
        {"tenant_id": "insurer-1"},
    )
    assert result["status"] == "non_binding"
    assert capability.requires_approval is False
