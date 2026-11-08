from typing import Any

from src.tools.account_tools import get_account_details


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_account_details",
            "description": (
                "Retrieve details of a bank account belonging "
                "to the authenticated customer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The bank account identifier.",
                    }
                },
                "required": ["account_id"],
                "additionalProperties": False,
            },
        },
    }
]


class BankingToolRegistry:
    """Execute only explicitly approved banking tools."""

    def __init__(self, authorized_customer_id: str):
        if (
            not isinstance(authorized_customer_id, str)
            or not authorized_customer_id.strip()
        ):
            raise ValueError("A trusted customer ID is required")

        self._authorized_customer_id = authorized_customer_id

    def execute(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        if tool_name != "get_account_details":
            return {
                "status": "error",
                "message": "Tool not permitted",
            }

        if not isinstance(arguments, dict):
            return {
                "status": "error",
                "message": "Tool arguments must be an object",
            }

        if set(arguments) != {"account_id"}:
            return {
                "status": "error",
                "message": "Invalid tool arguments",
            }

        return get_account_details(
            account_id=arguments["account_id"],
            authorized_customer_id=self._authorized_customer_id,
        )
