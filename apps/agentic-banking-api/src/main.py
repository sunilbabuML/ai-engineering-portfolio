from contextlib import asynccontextmanager
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag.retriever import BankingPolicyRetriever
from src.rag.rag_service import BankingRAGService
from src.llm.factory import get_llm_provider


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "accounts.json"
KNOWLEDGE_BASE = ROOT / "data" / "knowledge_base"

retriever = BankingPolicyRetriever(KNOWLEDGE_BASE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize once when the API starts.
    retriever.initialize()
    app.state.rag_service = BankingRAGService(
        retriever=retriever,
        llm_provider=get_llm_provider(),
        min_similarity=0.60,
    )
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

    return app.state.rag_service.answer(
        body.question,
        top_k=3,
    )
