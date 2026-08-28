# AgentSite

> The open foundation for the agent-native internet.

AgentSite explores what comes after the website: a company-hosted AI agent that understands a user's goal, performs authorized work, and returns a useful result.

Today, companies expose capabilities through websites, APIs, CLIs, and MCP servers. Those interfaces are valuable, but they still require users or other agents to understand the company's predefined commands and data model. AgentSite aims to make the company's agent itself the primary interface.

## Vision

In an agent-native world, a user should be able to ask an AI assistant:

> “Find me a suitable insurance plan, compare the coverage, and start the application.”

The assistant should delegate to the insurer's AgentSite. The AgentSite should understand the request, ask only the necessary questions, use the company's live systems, apply policy and authorization controls, and complete the work.

The long-term goal is not to wrap a website in a chatbot. It is to provide a trustworthy, observable, company-controlled agent runtime that can reason over the company's capabilities and safely take action.

## Core principles

- **Agent-first:** natural language goals are the primary interface.
- **Capability-aware:** the agent can discover and use approved business capabilities.
- **Action-capable:** it can complete work, not only answer questions.
- **Grounded:** responses and actions are based on authorized company data and systems.
- **Human-controlled:** consent, approvals, identity, and escalation are explicit.
- **Observable:** every decision, tool call, result, and side effect can be audited.
- **Interoperable:** APIs, CLIs, MCP, events, and legacy systems remain useful execution primitives.
- **Portable:** companies should be able to host and operate their own AgentSite.

## What this repository will become

This repository is the design and implementation home for:

1. An AgentSite protocol and manifest for describing an agent's identity, capabilities, policies, and endpoints.
2. A runtime that receives requests, plans work, calls approved capabilities, and produces grounded responses.
3. An adapter layer for APIs, CLIs, MCP servers, databases, queues, and internal systems.
4. Security controls for authentication, authorization, data boundaries, approvals, and tenant isolation.
5. Evaluation and observability tools for reliability, safety, cost, latency, and task completion.
6. Reference AgentSites that demonstrate practical company use cases.

## Proposed request flow

```text
User or external assistant
          |
          v
AgentSite discovery and trust
          |
          v
Agent runtime: understand -> plan -> request approval when needed
          |
          v
Capability adapters: API | CLI | MCP | database | workflow
          |
          v
Company systems and data
          |
          v
Grounded result, action receipt, and audit trail
```

## Status

This project is at the vision and foundation stage. The first milestone is to turn the concept into a small, inspectable reference implementation with a clear security model and a deliberately narrow execution surface.

See [ROADMAP.md](ROADMAP.md) for the current plan and [docs/architecture.md](docs/architecture.md) for the initial architecture.

## First implementation

The repository now contains a small Python reference runtime. It exposes only typed capabilities to the model and keeps company credentials and resource clients inside server-side adapters. A machine-readable discovery document is available in [`agentsite.manifest.json`](agentsite.manifest.json), and a local example can be started with:

```bash
python examples/local_agent.py
```

The resource boundary and connection patterns are described in [docs/resource-connection.md](docs/resource-connection.md). This is an early protocol/runtime experiment, not yet a production deployment package.

Reference business capabilities for ecommerce product search and insurance quote creation are in [`examples/business_capabilities.py`](examples/business_capabilities.py), with the conversation-to-capability model documented in [docs/conversation-to-capability.md](docs/conversation-to-capability.md).

## Contributing

The project is public and intended to be built openly. Start with the roadmap, open an issue to discuss substantial changes, and keep every capability explicit about its permissions, inputs, outputs, and side effects.

## License

License will be selected before the first production-ready release.
