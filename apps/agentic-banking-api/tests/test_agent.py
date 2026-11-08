from ollama import ResponseError, RequestError
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


@pytest.mark.parametrize(
    "exception_type",
    [ConnectionError, TimeoutError],
)
def test_initial_ollama_failure_returns_safe_error(
    exception_type,
):
    import json
    from unittest.mock import Mock

    agent = BankingAgent(
        authorized_customer_id="TEST-CUSTOMER"
    )

    agent.client.chat = Mock(
        side_effect=exception_type(
            "INTERNAL-SECRET: Ollama service failure"
        )
    )

    result = agent.run(
        "What is my account balance?"
    )

    assert result["mode"] == "agent_error"
    assert result["tool_used"] is None

    assert result["answer"] == (
        "The banking assistant is temporarily unavailable. "
        "Please try again later."
    )

    assert "INTERNAL-SECRET" not in json.dumps(result)
    assert agent.client.chat.call_count == 1


@pytest.mark.parametrize(
    "exception_type",
    [ConnectionError, TimeoutError],
)
def test_final_ollama_failure_returns_safe_error(
    exception_type,
):
    import json
    from unittest.mock import Mock

    agent = BankingAgent(
        authorized_customer_id="TEST-CUSTOMER"
    )

    tool_call = Mock()
    tool_call.function.name = "get_account_details"
    tool_call.function.arguments = {
        "account_id": "DEMO-1001"
    }

    first_response = Mock()
    first_response.message.tool_calls = [tool_call]
    first_response.message.model_dump.return_value = {
        "role": "assistant",
        "content": "",
    }

    agent.client.chat = Mock(
        side_effect=[
            first_response,
            exception_type(
                "INTERNAL-SECRET: Ollama service failure"
            ),
        ]
    )

    agent.registry.execute = Mock(
        return_value={
            "status": "success",
            "account": {
                "balance_usd": 999999.99,
            },
        }
    )

    result = agent.run(
        "What is my account balance?"
    )

    assert result["mode"] == "agent_error"
    assert result["tool_used"] == "get_account_details"

    assert result["answer"] == (
        "The banking assistant is temporarily unavailable. "
        "Please try again later."
    )

    raw_response = json.dumps(result)

    assert "INTERNAL-SECRET" not in raw_response
    assert "999999.99" not in raw_response

    assert agent.client.chat.call_count == 2
    assert agent.registry.execute.call_count == 1


@pytest.mark.parametrize(
    "exception_factory",
    [
        lambda: ResponseError(
            "INTERNAL-SECRET: Ollama server failure",
            status_code=500,
        ),
        lambda: RequestError(
            "INTERNAL-SECRET: Invalid Ollama request",
        ),
    ],
    ids=["ResponseError", "RequestError"],
)
def test_initial_ollama_specific_error_is_safe(
    exception_factory,
):
    import json
    from unittest.mock import Mock

    agent = BankingAgent(
        authorized_customer_id="TEST-CUSTOMER"
    )

    agent.client.chat = Mock(
        side_effect=exception_factory()
    )

    result = agent.run(
        "What is my account balance?"
    )

    assert result["mode"] == "agent_error"
    assert result["tool_used"] is None

    assert result["answer"] == (
        "The banking assistant is temporarily unavailable. "
        "Please try again later."
    )

    assert "INTERNAL-SECRET" not in json.dumps(result)
    assert agent.client.chat.call_count == 1


@pytest.mark.parametrize(
    "exception_factory",
    [
        lambda: ResponseError(
            "INTERNAL-SECRET: Ollama server failure",
            status_code=500,
        ),
        lambda: RequestError(
            "INTERNAL-SECRET: Invalid Ollama request",
        ),
    ],
    ids=["ResponseError", "RequestError"],
)
def test_final_ollama_specific_error_is_safe(
    exception_factory,
):
    import json
    from unittest.mock import Mock

    agent = BankingAgent(
        authorized_customer_id="TEST-CUSTOMER"
    )

    tool_call = Mock()
    tool_call.function.name = "get_account_details"
    tool_call.function.arguments = {
        "account_id": "DEMO-1001"
    }

    first_response = Mock()
    first_response.message.tool_calls = [tool_call]
    first_response.message.model_dump.return_value = {
        "role": "assistant",
        "content": "",
    }

    agent.client.chat = Mock(
        side_effect=[
            first_response,
            exception_factory(),
        ]
    )

    agent.registry.execute = Mock(
        return_value={
            "status": "success",
            "account": {
                "balance_usd": 999999.99,
            },
        }
    )

    result = agent.run(
        "What is my account balance?"
    )

    assert result["mode"] == "agent_error"
    assert result["tool_used"] == "get_account_details"

    assert result["answer"] == (
        "The banking assistant is temporarily unavailable. "
        "Please try again later."
    )

    raw_response = json.dumps(result)

    assert "INTERNAL-SECRET" not in raw_response
    assert "999999.99" not in raw_response

    assert agent.client.chat.call_count == 2
    assert agent.registry.execute.call_count == 1
