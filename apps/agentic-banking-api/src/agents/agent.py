from ollama import ResponseError, RequestError
import json

from ollama import Client

from src.audit.audit_logger import AgentAuditLogger

from src.tools.tool_registry import (
    BankingToolRegistry,
    TOOL_DEFINITIONS,
)


class BankingAgent:
    """Banking assistant with one tool call and a grounded final response."""

    def __init__(
        self,
        authorized_customer_id: str,
        model: str = "qwen2.5:3b",
        host: str = "http://localhost:11434",
        audit_logger: AgentAuditLogger | None = None,
    ):
        self.audit_logger = audit_logger or AgentAuditLogger()
        self.model = model
        self.client = Client(host=host, timeout=120.0)
        self.registry = BankingToolRegistry(authorized_customer_id)

    def run(self, question: str) -> dict:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("A non-empty question is required")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a banking assistant. "
                    "Use tools for account-specific questions. "
                    "Never invent account balances or customer data. "
                    "Only report account details returned by approved tools. "
                    "If access is denied, do not reveal account information."
                ),
            },
            {"role": "user", "content": question},
        ]

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                options={"temperature": 0},
            )
        except (ConnectionError, TimeoutError, OSError, ResponseError, RequestError):
            return {
                "question": question,
                "mode": "agent_error",
                "tool_used": None,
                "answer": (
                    "The banking assistant is temporarily unavailable. "
                    "Please try again later."
                ),
            }

        tool_calls = response.message.tool_calls or []

        if not tool_calls:
            return {
                "question": question,
                "mode": "agent_no_tool",
                "tool_used": None,
                "answer": response.message.content or "",
            }

        # Initial implementation permits only one tool call.
        if len(tool_calls) != 1:
            return {
                "question": question,
                "mode": "agent_error",
                "answer": "Unable to process multiple tool requests.",
            }

        tool_call = tool_calls[0]
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        try:
            tool_result = self.registry.execute(
                tool_name=tool_name,
                arguments=arguments,
            )
        except Exception:
            tool_result = {
                "status": "error",
                "message": "Unable to complete the banking request.",
            }

        try:
            self.audit_logger.log_tool_execution(
                tool_name=tool_name,
                status=tool_result.get("status", "error"),
            )
        except Exception:
            return {
                "question": question,
                "mode": "agent_error",
                "tool_used": tool_name,
                "answer": (
                    "The banking assistant is temporarily unavailable. "
                    "Please try again later."
                ),
            }

        # Never send unauthorized account data to the model.
        if tool_result.get("status") != "success":
            return {
                "question": question,
                "mode": "agent_tool_execution",
                "tool_used": tool_name,
                "tool_result": tool_result,
                "answer": tool_result.get(
                    "message",
                    "Unable to retrieve account details.",
                ),
            }

        messages.append(response.message.model_dump(exclude_none=True))

        messages.append(
            {
                "role": "tool",
                "tool_name": tool_name,
                "content": json.dumps(tool_result),
            }
        )

        try:
            final_response = self.client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0},
            )
        except (ConnectionError, TimeoutError, OSError, ResponseError, RequestError):
            return {
                "question": question,
                "mode": "agent_error",
                "tool_used": tool_name,
                "answer": (
                    "The banking assistant is temporarily unavailable. "
                    "Please try again later."
                ),
            }

        return {
            "question": question,
            "mode": "agent_with_tool_response",
            "tool_used": tool_name,
            "tool_arguments": arguments,
            "tool_result": tool_result,
            "answer": final_response.message.content or "",
        }
