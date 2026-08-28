# AgentSite Roadmap

This roadmap is intentionally staged: trust and execution boundaries come before broad autonomy.

## Phase 0 — Foundation

- [x] Create the public project and document the vision.
- [x] Define the initial AgentSite vocabulary and architecture.
- [ ] Choose the initial implementation language and model provider abstraction.
- [ ] Select an open-source license.
- [ ] Define the threat model and non-goals.

## Phase 1 — Minimal AgentSite

- [ ] Define an AgentSite manifest.
- [ ] Implement a request endpoint with streaming responses.
- [ ] Add a capability registry with typed input/output schemas.
- [ ] Implement one safe read-only reference capability.
- [ ] Add structured action receipts and correlation IDs.
- [ ] Add a local development CLI.

## Phase 2 — Safe execution

- [ ] Add authentication and per-capability authorization.
- [ ] Add approval checkpoints for consequential actions.
- [ ] Add secret isolation and outbound network policy.
- [ ] Add tenant and user data boundaries.
- [ ] Add retries, timeouts, idempotency, and cancellation.
- [ ] Add an audit log and trace viewer.

## Phase 3 — Interoperability

- [ ] Build adapters for REST/OpenAPI services.
- [ ] Build adapters for MCP servers.
- [ ] Build adapters for CLIs and asynchronous jobs.
- [ ] Define discovery and trust metadata for external assistants.
- [ ] Support handoff between AgentSites.

## Phase 4 — Production readiness

- [ ] Add evaluation suites for task completion and unsafe behavior.
- [ ] Add cost, latency, and reliability budgets.
- [ ] Add deployment templates for common cloud environments.
- [ ] Add policy-as-code and organization-level controls.
- [ ] Publish reference implementations for several industries.

## Product questions to resolve

- How should an external assistant verify that it is speaking to the real company AgentSite?
- Which actions require explicit user confirmation, and who defines that policy?
- How can an AgentSite expose enough capability for useful delegation without leaking internal structure?
- What should be standardized at the protocol layer versus left to the runtime?
- How should agents explain uncertainty, partial completion, and responsibility for side effects?
