import os

from openai import OpenAI


class OpenAIProvider:
    """LLM provider backed by the OpenAI Responses API."""

    def __init__(self, model: str = "gpt-4.1-mini"):
        self.model = model

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Set the environment variable before using OpenAIProvider."
            )

        self.client = OpenAI(timeout=60.0, max_retries=2)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate an answer using the OpenAI Responses API."""

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            temperature=0,
        )

        answer = response.output_text

        if not answer:
            raise RuntimeError("OpenAI returned an empty response.")

        return answer.strip()
