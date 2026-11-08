import json
from pathlib import Path

from src.tools.account_tools import get_account_details


ROOT = Path(__file__).resolve().parents[4]
TRANSACTIONS_FILE = ROOT / "data" / "transactions.json"


def get_transaction_history(
    account_id: str,
    authorized_customer_id: str,
    limit: int = 5,
) -> dict:
    """
    Retrieve synthetic transaction history for an authorized account.

    The customer identity must come from trusted application context.
    """

    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")

    # Verify ownership before accessing transaction data.
    account_result = get_account_details(
        account_id=account_id,
        authorized_customer_id=authorized_customer_id,
    )

    if account_result["status"] != "success":
        return {
            "status": "not_found",
            "message": "Account not found or access not permitted",
        }

    transactions = json.loads(
        TRANSACTIONS_FILE.read_text(encoding="utf-8")
    )

    account_transactions = [
        transaction
        for transaction in transactions
        if transaction["account_id"] == account_id
    ]

    account_transactions.sort(
        key=lambda transaction: (
            transaction["transaction_date"],
            transaction["transaction_id"],
        ),
        reverse=True,
    )

    selected_transactions = account_transactions[:limit]

    return {
        "status": "success",
        "account_id": account_id,
        "transaction_count": len(selected_transactions),
        "transactions": selected_transactions,
    }
