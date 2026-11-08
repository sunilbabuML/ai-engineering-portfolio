# AI Engineering Portfolio

A hands-on, seven-day AI engineering portfolio demonstrating retrieval-augmented generation (RAG), local large language models, agentic workflows, banking tool integration, safety controls, and automated testing.

The portfolio is organized around two project themes:

1. **Enterprise Agentic Banking AI** — RAG, tool calling, account authorization checks, transaction retrieval, and audit logging.
2. **AI Gateway, Evaluation & Observability** — Planned evaluation, monitoring, and reliability capabilities.

> **Project status:** Days 1–4 completed. Days 5–7 are in progress or planned.
>
> **Disclaimer:** This is an educational portfolio using synthetic banking data, not a production financial application.

## Portfolio Progress

| Day | Focus | Status |
|-----|-------|--------|
| Day 1 | FastAPI foundation and synthetic banking data | Completed |
| Day 2 | RAG retrieval and question answering | Completed |
| Day 3 | Agent orchestration and banking tool calling | Completed |
| Day 4 | Authorization safeguards, audit logging, validation, and failure handling | Completed |
| Day 5 | Evaluation, tracing, and observability | Planned |
| Day 6 | Integration, performance, and deployment | Planned |
| Day 7 | Portfolio polish and interview demonstrations | Planned |

## Completed Capabilities

### API and Banking Data
- FastAPI application with demonstration endpoints
- Synthetic customer account and transaction datasets
- Automated API tests

### Retrieval-Augmented Generation
- Banking knowledge base
- Retrieval-based question answering
- Local Ollama model integration

### Agentic AI
- Banking agent powered by `qwen2.5:3b`
- Structured LLM tool calling
- Account details retrieval
- Transaction history retrieval
- Python-controlled tool execution

### Safety and Reliability
- Account ownership validation
- Rejection of unauthorized account requests
- Tool argument validation
- Protection against customer identity injection through tool arguments
- Structured JSONL audit logging
- Controlled Ollama and banking tool error handling
- Controlled failure when audit logging is unsuccessful
- 49 passing automated tests at the latest confirmed regression run

## Project Documentation

| Resource | Description |
|----------|-------------|
| [Agentic Banking API README](apps/agentic-banking-api/README.md) | Detailed setup, banking tools, architecture, safeguards, and testing |
| [Architecture Documentation](docs/architecture.md) | Repository architecture and technical design |

## Quick Start

Python 3.11+ recommended.

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install Ollama and download the local model:

```powershell
ollama pull qwen2.5:3b
```

Start Ollama separately if it is not already running:

```powershell
ollama serve
```

Configure the banking application using `apps/agentic-banking-api/.env.example` as a reference.

Start FastAPI:

```powershell
cd apps/agentic-banking-api
python -m uvicorn src.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

Demonstration endpoints:

- `GET /health`
- `GET /demo/accounts`
- `POST /demo/ask`

The banking agent's tool-calling workflow is implemented separately; these API endpoints do not constitute a production authenticated banking interface.

## Testing

From `apps/agentic-banking-api`:

```powershell
python -m pytest tests/ -v
```

**Latest confirmed regression result: 49 tests passed.**

## Docker

The repository also includes the original Day 1 Docker workflow.

From the repository root:

```powershell
docker build -t ai-banking-day1 .
docker run --rm -p 8000:8000 ai-banking-day1
```

## Roadmap

### Days 1–4: Completed

Built the banking API foundation, RAG workflow, local LLM integration, agentic banking tools, authorization safeguards, audit logging, and automated regression tests.

### Day 5: Evaluation and Observability

Planned: evaluation datasets, tool-selection accuracy, response quality checks, latency measurement, and execution tracing.

### Day 6: Integration and Deployment

Planned: integration testing, performance validation, and deployment improvements.

### Day 7: Portfolio Presentation

Planned: final documentation, architecture walkthroughs, and interview-ready demonstrations.

## Data and Security

All banking records are synthetic. The prototype does not implement production authentication, financial transaction processing, or durable centralized audit storage.

Do not deploy publicly or connect to real customer accounts without substantial additional security engineering and review.
