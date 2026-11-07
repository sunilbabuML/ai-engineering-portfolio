from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Common interface for all language model providers."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response using a language model.

        Args:
            system_prompt: Instructions controlling model behavior.
            user_prompt: User question and retrieved RAG context.

        Returns:
            The generated answer as a string.
        """
        ...
