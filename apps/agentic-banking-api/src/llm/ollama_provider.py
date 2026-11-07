from ollama import Client


class OllamaProvider:
    """LLM provider backed by a locally running Ollama server."""

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.client = Client(host=host, timeout=120.0)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate an answer using the Ollama chat API."""

        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0},
        )

        content = response.message.content

        if not content:
            raise RuntimeError("Ollama returned an empty response.")

        return content.strip()
