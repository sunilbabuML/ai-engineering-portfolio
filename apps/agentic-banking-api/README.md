# Enterprise Agentic Banking AI

## Overview

A portfolio-grade agentic banking assistant built with Python, FastAPI, Ollama, and a local Qwen 2.5 model.

The application demonstrates LLM tool calling, retrieval-augmented generation (RAG), account ownership checks, structured audit logging, and controlled failure handling.

**This is an educational prototype using synthetic data, not a production banking system.**

## Architecture

```text
User Question
     |
     v
BankingAgent
     |
     v
Ollama / Qwen 2.5
     |
     v
LLM Tool Selection
     |
     v
BankingToolRegistry
     |
     +-- get_account_details
     |
     +-- get_transaction_history
     |
     v
Account Ownership Check
     |
     v
Synthetic Banking Data
     |
     v
Audit Logger
     |
     v
Ollama Final Response
     |
     v
User Answer
```

The final Ollama response is generated only when the tool execution and audit logging allow the workflow to continue.

## Technology Stack

- Python and FastAPI
- Ollama with `qwen2.5:3b`
- Local JSON banking datasets
- Sentence Transformers for RAG embeddings
- Pytest for automated regression testing
- Git and GitHub for version control

## Banking Tools

### get_account_details

Retrieves synthetic account details when the supplied account ID belongs to the trusted customer ID provided to the agent.

### get_transaction_history

Retrieves synthetic transaction history for an authorized account.

Supports a configurable result limit from 1 to 100.

Both tools are read-only.

## Safety and Reliability

The application demonstrates:

- Account ownership checks
- Rejection of unauthorized account access
- Rejection of customer identity injection through tool arguments
- Tool input validation
- Structured JSONL audit events
- Controlled responses for unexpected banking tool failures
- Controlled responses for Ollama connection errors and timeouts
- Handling of Ollama ResponseError and RequestError
- Controlled responses when audit logging fails
- Prevention of final answer generation when audit logging fails

The agent does not include internal exception details in its controlled error responses.

## Local Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install Ollama separately and download the model:

```powershell
ollama pull qwen2.5:3b
```

For the tested CPU-only Windows configuration, start Ollama in a separate PowerShell window:

```powershell
$env:CUDA_VISIBLE_DEVICES="-1"
$env:OLLAMA_LLM_LIBRARY="cpu"
ollama serve
```

Configure the application environment using `.env.example` as a reference.

Example:

```text
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_HOST=http://localhost:11434
```

## Run the API

From `apps/agentic-banking-api`:

```powershell
python -m uvicorn src.main:app --reload
```

Open:

http://127.0.0.1:8000/docs

Available demonstration endpoints include:

- `GET /health`
- `GET /demo/accounts`
- `POST /demo/ask`

The `/demo/ask` endpoint demonstrates the RAG question-answering workflow. The BankingAgent tool-calling workflow is implemented separately and is not presented as an authenticated public API endpoint.

## Run Automated Tests

From `apps/agentic-banking-api`:

```powershell
python -m pytest tests/ -v
```

Day 4 verified test suite: **49 passing tests**.

Coverage includes banking tools, API behavior, authorization checks, audit logging, input validation, and controlled exception handling.

## Important Limitations

- All banking records are synthetic.
- The trusted customer ID is manually supplied; real user authentication is not implemented.
- Audit logging is local JSONL, not a durable centralized audit service.
- Banking tools are read-only; no transfers or balance modifications are supported.
- Audit failures prevent a successful agent response but do not undo a completed tool execution.
- The application has not undergone production security review.
- Do not deploy publicly or connect to real financial accounts without substantial additional security controls.

## Portfolio Learning Outcomes

This project demonstrates practical AI engineering concepts:

1. Integrating a local LLM with Python applications.
2. Implementing structured tool calling.
3. Separating LLM decisions from trusted application authorization logic.
4. Building RAG-based question answering.
5. Creating structured audit events.
6. Handling infrastructure failures safely.
7. Developing automated regression tests for agentic workflows.
