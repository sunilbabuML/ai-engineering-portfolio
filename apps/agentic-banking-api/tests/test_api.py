import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="module")
def client():
    """Initialize the RAG engine once for this test module."""
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_accounts(client):
    response = client.get("/demo/accounts")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_ask_retrieves_savings_policy(client):
    response = client.post(
        "/demo/ask",
        json={
            "question": "What is the monthly maintenance fee for a savings account?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "rag_retrieval"
    assert "$5" in data["answer"]
    assert len(data["citations"]) > 0
    assert data["citations"][0]["document_id"] == "BANK-POL-002"
    assert data["citations"][0]["source"] == "savings_account_policy.md"


def test_ask_retrieves_atm_limit(client):
    response = client.post(
        "/demo/ask",
        json={
            "question": "What is the daily ATM withdrawal limit for checking accounts?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "rag_retrieval"
    assert "$500" in data["answer"]
    assert data["citations"][0]["document_id"] == "BANK-POL-003"


def test_ask_rejects_empty_question(client):
    response = client.post(
        "/demo/ask",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_ask_rejects_whitespace_question(client):
    response = client.post(
        "/demo/ask",
        json={"question": "   "},
    )

    assert response.status_code == 422
