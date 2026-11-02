from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

app = FastAPI(title='Enterprise Agentic Banking AI', version='0.1.0')
DATA = Path(__file__).resolve().parents[3] / 'data' / 'accounts.json'

class Question(BaseModel):
    question: str

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'agentic-banking-api'}

@app.get('/demo/accounts')
def accounts():
    return json.loads(DATA.read_text())

@app.post('/demo/ask')
def ask(body: Question):
    return {'question': body.question, 'answer': 'Agent and RAG implementation planned for Days 2–3.', 'mode': 'stub', 'citations': []}
