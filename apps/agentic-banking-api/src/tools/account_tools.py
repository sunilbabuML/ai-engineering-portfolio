import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ACCOUNTS_FILE = ROOT / "data" / "accounts.json"


def get_account_details(account_id: str, authorized_customer_id: str) -> dict:
    """
    Retrieve a synthetic bank account belonging to an authorized customer.

    authorized_customer_id must come from a trusted application context,
    never from an LLM-generated tool argument.
    """
    if not isinstance(account_id, str) or not account_id.strip():
        raise ValueError("A valid account_id is required")

    if not isinstance(authorized_customer_id, str) or not authorized_customer_id.strip():
        raise ValueError("An authorized customer ID is required")

    accounts = json.loads(
        ACCOUNTS_FILE.read_text(encoding="utf-8")
    )

    for account in accounts:
        if (
            account["account_id"] == account_id
            and account["customer_id"] == authorized_customer_id
        ):
            return {
                "status": "success",
                "account": {
                    "account_id": account["account_id"],
                    "account_type": account["account_type"],
                    "balance_usd": account["balance_usd"],
                    "currency": account["currency"],
                },
            }

    return {
        "status": "not_found",
        "message": "Account not found or access not permitted",
    }
