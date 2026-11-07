import os

from dotenv import load_dotenv

from src.llm.base import LLMProvider
from src.llm.ollama_provider import OllamaProvider


def get_llm_provider() -> LLMProvider:
    """Create an LLM provider based on environment configuration."""

    load_dotenv()

    provider_name = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider_name == "ollama":
        return OllamaProvider(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        )

    if provider_name == "openai":
        from src.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider_name}. "
        "Supported providers: ollama, openai."
    )
