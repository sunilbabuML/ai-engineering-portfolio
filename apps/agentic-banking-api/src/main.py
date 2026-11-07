from contextlib import asynccontextmanager
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag.retriever import BankingPolicyRetriever


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "accounts.json"
KNOWLEDGE_BASE = ROOT / "data" / "knowledge_base"

retriever = BankingPolicyRetriever(KNOWLEDGE_BASE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize once when the API starts.
    retriever.initialize()
    yield


app = FastAPI(
    title="Enterprise Agentic Banking AI",
    version="0.2.0",
    lifespan=lifespan,
)


class Question(BaseModel):
    question: str = Field(min_length=1)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "agentic-banking-api",
    }


@app.get("/demo/accounts")
def accounts():
    return json.loads(DATA.read_text(encoding="utf-8"))


@app.post("/demo/ask")
def ask(body: Question):
    if not body.question.strip():
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty",
        )

    results = retriever.retrieve(
        body.question,
        top_k=3,
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No relevant policies found",
        )

    top_result = results[0]

    citations = [
        {
            "document_id": result["metadata"]["document_id"],
            "source": result["source"],
            "chunk_id": result["chunk_id"],
            "similarity": round(result["score"], 4),
        }
        for result in results
    ]

    return {
        "question": body.question,
        "answer": top_result["content"],
        "mode": "rag_retrieval",
        "citations": citations,
    }
