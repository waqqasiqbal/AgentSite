# From customer conversation to company action

Customers can ask for outcomes in ordinary language:

- “Show me noise-cancelling headphones under €150 and tell me which are in stock.”
- “I need travel insurance for a two-week trip to Spain. Create a quote.”
- “Compare the available plans and explain the difference in price and coverage.”

The model translates the request into one or more typed capabilities. It does not invent database queries or call arbitrary company systems.

| Customer goal | Capability | Default behavior |
|---|---|---|
| Find products and prices | `catalog.search_products` | Read-only, current catalog data |
| Inspect product details | `catalog.get_product` | Read-only, filtered fields |
| Create a non-binding quote | `insurance.create_quote` | Allowed after required details are collected |
| Buy a product | `orders.create` | Explicit confirmation and idempotency required |
| Bind an insurance policy | `insurance.bind_policy` | Strong approval and payment/identity checks |

## Conversation loop

1. The AgentSite receives the user's goal and authenticated tenant/user context.
2. The LLM asks a clarification question when required fields are missing.
3. The LLM proposes a typed capability call.
4. AgentSite validates the arguments and applies policy.
5. The server-side adapter queries the relevant company system.
6. Only the minimum useful result returns to the model, with provenance and status.
7. The model explains the result or asks for approval before the next consequential step.

“Create a quote” should be non-binding by default. If the company treats quote creation as a regulated, paid, or binding action, its capability should declare `requires_approval: true` and use stronger identity and consent checks.

“Ask anything” does not mean unrestricted access. The agent should answer from the company's approved knowledge and capabilities, say when it cannot complete a request, and offer a human handoff when appropriate.
