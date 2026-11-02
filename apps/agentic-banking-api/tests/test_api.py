from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_demo_accounts():
    response = client.get('/demo/accounts')
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_ask_is_explicit_stub():
    response = client.post('/demo/ask', json={'question':'What is the checking balance?'})
    assert response.status_code == 200
    assert response.json()['mode'] == 'stub'
