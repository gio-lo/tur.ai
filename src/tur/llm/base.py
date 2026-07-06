"""Core LLM interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol, Sequence


@dataclass(slots=True, frozen=True)
class ChatMessage:
    """Represents one chat message passed to the LLM."""

    role: str
    content: str


class LLMClient(Protocol):
    """Provider-agnostic interface for chat completion."""

    def generate_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        """Generate an assistant reply for the given conversation."""

    def stream_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> Iterator[str]:
        """Stream an assistant reply for the given conversation."""
