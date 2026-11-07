import pytest
from fastapi.testclient import TestClient

from src.main import app


class FakeLLMProvider:
    """Deterministic LLM substitute for automated tests."""

    def __init__(self):
        self.calls = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        })

        if "monthly maintenance fee for a savings account" in user_prompt.lower():
            return "The monthly maintenance fee for a savings account is $5."

        if "daily atm withdrawal limit for checking accounts" in user_prompt.lower():
            return "The daily ATM withdrawal limit for checking accounts is $500."

        return "No matching test response configured."


@pytest.fixture(scope="module")
def client():
    """Initialize FastAPI and replace the LLM with a deterministic fake."""
    with TestClient(app) as test_client:
        fake_provider = FakeLLMProvider()
        original_provider = app.state.rag_service.llm_provider

        app.state.rag_service.llm_provider = fake_provider

        try:
            yield test_client, fake_provider
        finally:
            app.state.rag_service.llm_provider = original_provider


def test_health(client):
    test_client, _ = client
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_accounts(client):
    test_client, _ = client
    response = test_client.get("/demo/accounts")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_ask_generates_savings_answer(client):
    test_client, _ = client

    response = test_client.post(
        "/demo/ask",
        json={
            "question": "What is the monthly maintenance fee for a savings account?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "rag_generation"
    assert "$5" in data["answer"]
    assert len(data["citations"]) == 1
    assert data["citations"][0]["document_id"] == "BANK-POL-002"
    assert data["citations"][0]["source"] == "savings_account_policy.md"


def test_ask_generates_atm_answer(client):
    test_client, _ = client

    response = test_client.post(
        "/demo/ask",
        json={
            "question": "What is the daily ATM withdrawal limit for checking accounts?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "rag_generation"
    assert "$500" in data["answer"]
    assert data["citations"][0]["document_id"] == "BANK-POL-003"


def test_ask_rejects_empty_question(client):
    test_client, _ = client

    response = test_client.post(
        "/demo/ask",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_ask_rejects_whitespace_question(client):
    test_client, _ = client

    response = test_client.post(
        "/demo/ask",
        json={"question": "   "},
    )

    assert response.status_code == 422


def test_unsupported_question_skips_llm(client):
    test_client, fake_provider = client

    calls_before = len(fake_provider.calls)

    response = test_client.post(
        "/demo/ask",
        json={
            "question": "What is the bank's policy on cryptocurrency trading?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "rag_generation"
    assert "could not find" in data["answer"].lower()
    assert data["citations"] == []
    assert len(fake_provider.calls) == calls_before


def test_generated_answer_comes_from_llm(client):
    test_client, fake_provider = client

    calls_before = len(fake_provider.calls)

    response = test_client.post(
        "/demo/ask",
        json={
            "question": "What is the monthly maintenance fee for a savings account?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "The monthly maintenance fee for a savings account is $5."
    )
    assert len(fake_provider.calls) == calls_before + 1

    prompt = fake_provider.calls[-1]["user_prompt"]

    assert "BANK-POL-002" in prompt
    assert "Banking policy context:" in prompt
