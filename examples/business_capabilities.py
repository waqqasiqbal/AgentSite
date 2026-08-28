"""Reference capability contracts for ecommerce and insurance AgentSites.

These adapters use in-memory data only. In a real deployment, replace the
functions with tenant-scoped calls to the company's systems.
"""

from agentsite.capabilities import Capability, CapabilityRegistry


PRODUCTS = [
    {"id": "p_100", "name": "Noise-cancelling headphones", "category": "electronics", "price": 129.0, "currency": "EUR", "stock": 12},
    {"id": "p_101", "name": "Travel backpack", "category": "travel", "price": 89.0, "currency": "EUR", "stock": 4},
]


def search_products(arguments, context):
    query = arguments["query"].lower()
    category = arguments.get("category")
    return [
        product
        for product in PRODUCTS
        if query in product["name"].lower()
        and (category is None or product["category"] == category)
    ][: arguments.get("limit", 10)]


def create_quote(arguments, context):
    # A real adapter would validate the applicant, call the insurer's rating
    # service, and return a quote reference plus an expiry timestamp.
    return {
        "quote_id": "quote_demo_001",
        "status": "non_binding",
        "product": arguments["insurance_product"],
        "annual_premium": 420.0,
        "currency": "EUR",
        "tenant_id": context["tenant_id"],
    }


def build_reference_registry() -> CapabilityRegistry:
    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="catalog.search_products",
            description="Find products and current prices in the authenticated store.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "category": {"type": "string"},
                    "limit": {"type": "number"},
                },
                "required": ["query"],
            },
            execute=search_products,
        )
    )
    registry.register(
        Capability(
            name="insurance.create_quote",
            description="Create a non-binding insurance quote from supplied customer details.",
            input_schema={
                "type": "object",
                "properties": {
                    "insurance_product": {"type": "string"},
                    "customer_details": {"type": "object"},
                },
                "required": ["insurance_product", "customer_details"],
            },
            execute=create_quote,
            risk="financial_quote",
            requires_approval=False,
        )
    )
    return registry
