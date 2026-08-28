# How an AgentSite connects to company resources

The LLM should not connect directly to a company's database, file store, SaaS account, or network. AgentSite places a controlled execution boundary between the model and those resources.

```text
External assistant/user
        |
        v
AgentSite edge: identity, tenant, rate limit, trace
        |
        v
LLM: receives request + safe capability definitions
        |
        v
Policy engine: validates identity, scope, risk, approval
        |
        v
Capability adapter: server-side credentials and query logic
        |
        v
Company resources: APIs, files, databases, queues, SaaS, workflows
```

## Resource patterns

### Data and databases

Expose business operations such as `customers.lookup` or `orders.list`, not unrestricted SQL. The adapter owns connection pooling, row-level tenant filters, pagination, redaction, and query limits. If natural-language analytics are needed, compile to a restricted query plan and validate it before execution.

### Files

Expose search, metadata retrieval, and bounded content extraction. Pass the model only the minimum relevant excerpts, with document IDs and citations. Enforce tenant, folder, classification, and malware/content checks in the adapter.

### APIs and SaaS systems

Wrap each approved operation as a capability. Keep OAuth tokens and API keys server-side. Separate read and write capabilities, declare side effects, enforce idempotency, and require approval for consequential actions.

### CLI, MCP, queues, and workflows

Treat them as adapters rather than trusted model tools. Use allowlists, isolated processes, timeouts, output-size limits, structured schemas, and cancellation. Never pass arbitrary shell text or unrestricted MCP access to the model.

## Context rules

The model sees capability descriptions and filtered results—not credentials, unrestricted connections, or entire company datasets. Every result should carry provenance, sensitivity metadata, and a trace ID. Memory is opt-in, tenant-scoped, reviewable, and deletable.

## The first implementation

The initial runtime in `src/agentsite` implements this contract without tying the core to a model vendor. A provider returns either a final answer or typed `ToolCall` objects. The runtime validates arguments, asks the policy engine for a decision, executes the server-side adapter, and returns a structured `ToolResult` to the provider.

The next production layers are an HTTP transport, authentication, persistent audit events, real provider adapters, and a hardened sandbox for higher-risk tools.
