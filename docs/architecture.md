# Enterprise Agentic AI Architecture (planned)

```mermaid
flowchart TD
    U[Web UI] --> API[FastAPI + Auth]
    API --> G[LLM Gateway / Routing]
    G --> A[LangGraph Agent]
    A --> R[RAG Retrieval]
    A --> T[Authorized SQL / MCP Tools]
    R --> V[(Vector Store)]
    T --> DB[(Synthetic Banking DB)]
    A --> L[LLM Provider]
    API --> O[Evaluation + Tracing + Cost]
```

## Day 1 implemented
- FastAPI health endpoint, synthetic account data endpoint, explicit placeholder question endpoint.
- Local test scaffolding and container configuration.

## Not yet implemented
- Authentication and authorization, actual RAG, agent planning, MCP, model routing, evaluation, monitoring and production hardening.

## Security decisions
- All accounts are fabricated. Never commit credentials or real customer data.
- Day 1 `/demo/accounts` is intentionally unauthenticated and must not be used for sensitive data.
- Future tools will be read-only and subject to per-user access controls.
