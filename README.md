# AI Engineering Portfolio

Two reusable projects: (1) Enterprise Agentic Banking AI and (2) AI Gateway, Evaluation & Observability. This repository is a seven-day learning portfolio, **not** a production banking application.

## Day 1: Quick start

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cd apps/agentic-banking-api
python -m uvicorn src.main:app --reload
```

Visit http://127.0.0.1:8000/docs and try `GET /health`, `GET /demo/accounts`, and `POST /demo/ask`.

Run tests from `apps/agentic-banking-api`:

```bash
python -m pytest -q
```

Or run from the repository root using Docker:

```bash
docker build -t ai-banking-day1 .
docker run --rm -p 8000:8000 ai-banking-day1
```

## Architecture
See [architecture](docs/architecture.md).

## Roadmap
- Day 2: RAG retrieval with citations.
- Day 3: Agent orchestration, tool calling and state.
- Day 4: Gateway and safety controls.
- Day 5: Evaluation, tracing and cost metrics.
- Day 6: Integration, performance and deployment.
- Day 7: Portfolio documentation and interview demos.

## Data and security
Only synthetic data. The Day 1 API is an unauthenticated educational stub; do not deploy it publicly or connect it to real accounts.
