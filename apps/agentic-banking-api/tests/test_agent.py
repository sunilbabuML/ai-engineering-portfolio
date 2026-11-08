import json
from types import SimpleNamespace

import pytest

from src.agents.agent import BankingAgent
from src.tools.account_tools import ACCOUNTS_FILE


@pytest.fixture
def account():
    accounts = json.loads(
        ACCOUNTS_FILE.read_text(encoding="utf-8")
    )
    return accounts[0]


def make_response(content="", tool_calls=None):
    message = SimpleNamespace(
        content=content,
        tool_calls=tool_calls or [],
    )

    # Matches the interface used by BankingAgent.
    message.model_dump = lambda exclude_none=True: {
        "role": "assistant",
        "content": content,
        "tool_calls": [
            {
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                }
            }
            for call in (tool_calls or [])
        ],
    }

    return SimpleNamespace(message=message)


def make_tool_call(account_id):
    return SimpleNamespace(
        function=SimpleNamespace(
            name="get_account_details",
            arguments={"account_id": account_id},
        )
    )


class FakeOllamaClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("Unexpected additional LLM call")
        return self.responses.pop(0)


def test_authorized_account_lookup(account):
    agent = BankingAgent(
        authorized_customer_id=account["customer_id"]
    )

    fake_client = FakeOllamaClient([
        make_response(
            tool_calls=[make_tool_call(account["account_id"])]
        ),
        make_response(content="Your account balance is available."),
    ])

    agent.client = fake_client

    result = agent.run("What is my account balance?")

    assert result["mode"] == "agent_with_tool_response"
    assert result["tool_used"] == "get_account_details"
    assert result["tool_result"]["status"] == "success"
    assert (
        result["tool_result"]["account"]["balance_usd"]
        == account["balance_usd"]
    )
    assert len(fake_client.calls) == 2


def test_unauthorized_account_lookup(account):
    agent = BankingAgent(
        authorized_customer_id="UNAUTHORIZED-CUSTOMER"
    )

    fake_client = FakeOllamaClient([
        make_response(
            tool_calls=[make_tool_call(account["account_id"])]
        )
    ])

    agent.client = fake_client

    result = agent.run("What is the account balance?")

    assert result["tool_result"]["status"] == "not_found"
    assert "account" not in result["tool_result"]
    assert str(account["balance_usd"]) not in result["answer"]
    assert len(fake_client.calls) == 1


def test_agent_without_tool_call(account):
    agent = BankingAgent(
        authorized_customer_id=account["customer_id"]
    )

    fake_client = FakeOllamaClient([
        make_response(content="I can help with banking questions.")
    ])

    agent.client = fake_client

    result = agent.run("Hello")

    assert result["mode"] == "agent_no_tool"
    assert result["tool_used"] is None
    assert result["answer"] == "I can help with banking questions."


def test_multiple_tool_calls_rejected(account):
    agent = BankingAgent(
        authorized_customer_id=account["customer_id"]
    )

    fake_client = FakeOllamaClient([
        make_response(
            tool_calls=[
                make_tool_call(account["account_id"]),
                make_tool_call(account["account_id"]),
            ]
        )
    ])

    agent.client = fake_client

    result = agent.run("Check two accounts")

    assert result["mode"] == "agent_error"
    assert len(fake_client.calls) == 1


def test_empty_question_rejected(account):
    agent = BankingAgent(
        authorized_customer_id=account["customer_id"]
    )

    with pytest.raises(ValueError):
        agent.run("   ")
