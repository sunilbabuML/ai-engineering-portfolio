import json
from types import SimpleNamespace

import pytest

from src.agents.agent import BankingAgent
from src.audit.audit_logger import AgentAuditLogger


class FakeOllamaClient:
    def __init__(self, tool_name):
        self.tool_name = tool_name

    def chat(self, **kwargs):
        if "tools" in kwargs:
            tool_call = SimpleNamespace(
                function=SimpleNamespace(
                    name=self.tool_name,
                    arguments={"account_id": "DEMO-1001"},
                )
            )
            message = SimpleNamespace(
                tool_calls=[tool_call],
                content="",
            )
        else:
            message = SimpleNamespace(
                tool_calls=[],
                content="Request completed.",
            )

        message.model_dump = lambda **kwargs: {
            "role": "assistant",
            "content": "",
        }

        return SimpleNamespace(message=message)


@pytest.mark.parametrize(
    "tool_name,tool_status",
    [
        ("get_account_details", "success"),
        ("get_transaction_history", "success"),
        ("get_account_details", "not_found"),
        ("get_transaction_history", "not_found"),
        ("get_account_details", "error"),
    ],
)
def test_agent_audit_logging(
    tmp_path,
    monkeypatch,
    tool_name,
    tool_status,
):
    log_file = tmp_path / "agent_audit.jsonl"
    audit_logger = AgentAuditLogger(log_file)

    try:
        agent = BankingAgent(
            authorized_customer_id="TEST-CUSTOMER",
            audit_logger=audit_logger,
        )

        agent.client = FakeOllamaClient(tool_name)

        sensitive_result = {
            "status": tool_status,
            "balance_usd": 999999.99,
            "customer_id": "PRIVATE-CUSTOMER-ID",
            "transactions": [
                {"description": "PRIVATE-TRANSACTION"}
            ],
        }

        monkeypatch.setattr(
            agent.registry,
            "execute",
            lambda **kwargs: sensitive_result,
        )

        agent.run("Show my banking information")

        records = [
            json.loads(line)
            for line in log_file.read_text(
                encoding="utf-8"
            ).splitlines()
        ]

        assert len(records) == 1

        event = records[0]

        assert event["event_type"] == "banking_tool_execution"
        assert event["tool_name"] == tool_name
        assert event["status"] == tool_status
        assert "timestamp" in event

        assert set(event) == {
            "timestamp",
            "event_type",
            "tool_name",
            "status",
        }

        raw_log = log_file.read_text(encoding="utf-8")

        assert "999999.99" not in raw_log
        assert "PRIVATE-CUSTOMER-ID" not in raw_log
        assert "PRIVATE-TRANSACTION" not in raw_log
        assert "Show my banking information" not in raw_log

    finally:
        audit_logger.close()


@pytest.mark.parametrize(
    "tool_name",
    ["get_account_details", "get_transaction_history"],
)
def test_agent_handles_unexpected_tool_exception(
    tmp_path,
    monkeypatch,
    tool_name,
):
    log_file = tmp_path / "exception_audit.jsonl"
    audit_logger = AgentAuditLogger(log_file)

    try:
        agent = BankingAgent(
            authorized_customer_id="TEST-CUSTOMER",
            audit_logger=audit_logger,
        )

        agent.client = FakeOllamaClient(tool_name)

        def failing_tool(**kwargs):
            raise RuntimeError(
                "INTERNAL-SECRET: database connection failed"
            )

        monkeypatch.setattr(
            agent.registry,
            "execute",
            failing_tool,
        )

        result = agent.run("What is my account balance?")

        assert result["mode"] == "agent_tool_execution"
        assert result["tool_used"] == tool_name

        assert result["tool_result"] == {
            "status": "error",
            "message": "Unable to complete the banking request.",
        }

        assert result["answer"] == (
            "Unable to complete the banking request."
        )

        raw_response = json.dumps(result)

        assert "INTERNAL-SECRET" not in raw_response
        assert "database connection failed" not in raw_response

        records = [
            json.loads(line)
            for line in log_file.read_text(
                encoding="utf-8"
            ).splitlines()
        ]

        assert len(records) == 1
        assert records[0]["tool_name"] == tool_name
        assert records[0]["status"] == "error"

        raw_log = log_file.read_text(encoding="utf-8")

        assert "INTERNAL-SECRET" not in raw_log
        assert "database connection failed" not in raw_log

        # Failed tool execution must not trigger another LLM call.
        # The fake client would otherwise generate a final response.
        assert result["mode"] != "agent_with_tool_response"

    finally:
        audit_logger.close()
