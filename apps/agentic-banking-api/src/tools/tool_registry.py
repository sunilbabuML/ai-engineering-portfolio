from typing import Any

from src.tools.account_tools import get_account_details
from src.tools.transaction_tools import get_transaction_history


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_account_details",
            "description": (
                "Retrieve account details, including balance, "
                "for an account owned by the authenticated customer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Bank account identifier",
                    }
                },
                "required": ["account_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_transaction_history",
            "description": (
                "Retrieve recent transactions for an account "
                "owned by the authenticated customer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Bank account identifier",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions, 1 to 100",
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": ["account_id"],
                "additionalProperties": False,
            },
        },
    },
]


class BankingToolRegistry:
    """Execute approved banking tools under a trusted customer identity."""

    def __init__(self, authorized_customer_id: str):
        if (
            not isinstance(authorized_customer_id, str)
            or not authorized_customer_id.strip()
        ):
            raise ValueError("A trusted customer ID is required")

        self._authorized_customer_id = authorized_customer_id

    def execute(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        if not isinstance(arguments, dict):
            return {
                "status": "error",
                "message": "Tool arguments must be an object",
            }

        if tool_name == "get_account_details":
            if set(arguments) != {"account_id"}:
                return {
                    "status": "error",
                    "message": "Invalid tool arguments",
                }

            if not isinstance(arguments["account_id"], str):
                return {
                    "status": "error",
                    "message": "Invalid account ID",
                }

            return get_account_details(
                account_id=arguments["account_id"],
                authorized_customer_id=self._authorized_customer_id,
            )

        if tool_name == "get_transaction_history":
            if not {"account_id"} <= set(arguments):
                return {
                    "status": "error",
                    "message": "Missing account ID",
                }

            if not set(arguments) <= {"account_id", "limit"}:
                return {
                    "status": "error",
                    "message": "Invalid tool arguments",
                }

            if not isinstance(arguments["account_id"], str):
                return {
                    "status": "error",
                    "message": "Invalid account ID",
                }

            limit = arguments.get("limit", 5)

            if type(limit) is not int or not 1 <= limit <= 100:
                return {
                    "status": "error",
                    "message": "Invalid transaction limit",
                }

            return get_transaction_history(
                account_id=arguments["account_id"],
                authorized_customer_id=self._authorized_customer_id,
                limit=limit,
            )

        return {
            "status": "error",
            "message": "Tool not permitted",
        }
