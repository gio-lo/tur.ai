"""Fallback client used when no API key is configured."""

from __future__ import annotations

from typing import Iterator, Sequence

from tur.llm.base import ChatMessage, LLMClient


class DevelopmentLLMClient(LLMClient):
    """Deterministic fallback that keeps the app usable without credentials."""

    def generate_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        """Generate a deterministic fallback reply."""
        last_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "",
        )
        return (
            "Development mode is active because no OpenAI API key is configured. "
            f"I received: {last_user_message}"
        )

    def stream_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> Iterator[str]:
        """Stream the deterministic fallback as a single chunk."""
        yield self.generate_reply(system_prompt, messages)
