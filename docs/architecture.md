# Initial Architecture

AgentSite is a company-controlled agent boundary. It is not a replacement for every existing interface; it is the reasoning and delegation layer that makes those interfaces usable by an agent.

## Components

### 1. Edge and identity

Receives requests from users, external assistants, or other AgentSites. It authenticates the caller, establishes tenant and user context, applies rate limits, and creates a trace.

### 2. Agent runtime

Interprets the request, retrieves relevant context, plans a task, selects capabilities, and synthesizes the result. The runtime must distinguish proposed actions from completed actions and must never claim a side effect that was not confirmed by an execution result.

### 3. Capability registry

Describes approved operations using stable names, schemas, permissions, risk levels, and side-effect metadata. Capabilities should be narrow enough to authorize and test independently.

Example metadata:

```yaml
name: orders.create
description: Create an order after the user has reviewed the final total.
risk: consequential
requires_approval: true
input_schema: ./schemas/orders.create.input.json
output_schema: ./schemas/orders.create.output.json
idempotency: required
```

### 4. Adapter layer

Translates a capability call into the company's existing systems: REST APIs, OpenAPI services, MCP servers, CLIs, queues, databases, or internal workflows. Adapters should not silently broaden permissions or invent missing data.

### 5. Policy and approval engine

Evaluates identity, role, data scope, risk, spending limits, and approval requirements before execution. Policy decisions should be returned as structured events and recorded in the audit trail.

### 6. State, memory, and context

Provides only the context needed for the current task. Long-lived memory must be explicit, user-scoped or tenant-scoped, reviewable, and deletable. Sensitive data should not enter model context unless policy permits it.

### 7. Observability and audit

Records request IDs, model decisions, capability calls, policy decisions, approvals, outputs, errors, and side effects. Logs must be redacted and access-controlled while remaining useful for investigation.

## Execution contract

Every capability invocation should produce a structured result containing:

- invocation ID and request ID;
- capability name and version;
- normalized input and redaction metadata;
- authorization and approval status;
- execution status: proposed, approved, started, completed, failed, or cancelled;
- output or error classification;
- idempotency key and external transaction reference when applicable.

## Design boundary

The model proposes and interprets. The policy engine authorizes. The adapter executes. The system records what happened. Keeping these responsibilities distinct is essential for safety, testing, and vendor portability.

## Early non-goals

- Fully autonomous control of arbitrary company systems.
- Unbounded model-generated code with production access.
- Replacing existing APIs or MCP servers on day one.
- Treating a conversational response as proof that an action completed.
- Storing unrestricted company data in model memory.
