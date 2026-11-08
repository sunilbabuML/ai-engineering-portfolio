import json

import pytest

from src.tools.account_tools import ACCOUNTS_FILE
from src.tools.transaction_tools import get_transaction_history
from src.tools.tool_registry import BankingToolRegistry


@pytest.fixture
def account():
    return json.loads(
        ACCOUNTS_FILE.read_text(encoding="utf-8")
    )[0]


def test_authorized_transaction_history(account):
    result = get_transaction_history(
        account["account_id"],
        account["customer_id"],
        limit=3,
    )

    assert result["status"] == "success"
    assert result["transaction_count"] == 3
    assert len(result["transactions"]) == 3
    assert all(
        txn["account_id"] == account["account_id"]
        for txn in result["transactions"]
    )


def test_transactions_sorted_newest_first(account):
    result = get_transaction_history(
        account["account_id"],
        account["customer_id"],
        limit=100,
    )

    dates = [
        txn["transaction_date"]
        for txn in result["transactions"]
    ]

    assert dates == sorted(dates, reverse=True)


def test_unauthorized_transaction_access(account):
    result = get_transaction_history(
        account["account_id"],
        "UNAUTHORIZED-CUSTOMER",
    )

    assert result["status"] == "not_found"
    assert "transactions" not in result


@pytest.mark.parametrize("limit", [0, -1, 101, "5", True, None])
def test_invalid_transaction_limits(account, limit):
    with pytest.raises(ValueError):
        get_transaction_history(
            account["account_id"],
            account["customer_id"],
            limit=limit,
        )


def test_registry_rejects_identity_injection(account):
    registry = BankingToolRegistry(account["customer_id"])

    result = registry.execute(
        "get_transaction_history",
        {
            "account_id": account["account_id"],
            "authorized_customer_id": "OTHER-CUSTOMER",
        },
    )

    assert result["status"] == "error"


def test_registry_rejects_unknown_tool(account):
    registry = BankingToolRegistry(account["customer_id"])

    result = registry.execute(
        "delete_account",
        {"account_id": account["account_id"]},
    )

    assert result["status"] == "error"
