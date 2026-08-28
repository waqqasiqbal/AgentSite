"""Run a tiny local AgentSite: python examples/local_agent.py"""

from agentsite.capabilities import Capability, CapabilityRegistry
from agentsite.manifest import load_manifest
from agentsite.provider import ScriptedProvider
from agentsite.models import ModelTurn
from agentsite.runtime import AgentRuntime
from agentsite.transport import serve


def lookup_customer(arguments, context):
    # Replace this with a server-side query using context["tenant_id"].
    # Credentials and the underlying database client stay inside this adapter.
    records = {"ayan@example.com": {"name": "Ayan", "status": "active"}}
    return records.get(arguments["email"], {"found": False})


registry = CapabilityRegistry()
registry.register(
    Capability(
        name="customers.lookup",
        description="Look up a customer by email within the authenticated tenant.",
        input_schema={
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
        execute=lookup_customer,
    )
)

# Replace ScriptedProvider with an adapter for the chosen LLM provider.
provider = ScriptedProvider([ModelTurn(assistant_text="The local AgentSite is ready.")])
runtime = AgentRuntime(provider, registry)
serve(runtime, load_manifest("agentsite.manifest.json"))
