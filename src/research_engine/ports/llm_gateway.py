"""LLM Gateway protocol for AI model access.

Abstract interface for calling language models. Adapters swap
between direct SDK calls (R1) and platform AI gateway (R2+).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LlmGateway(Protocol):
    """Protocol for LLM access."""

    def complete(self, prompt: str) -> str:
        """Send a prompt and get a completion.

        Args:
            prompt: The prompt text.

        Returns:
            The model's response text.
        """
        ...
