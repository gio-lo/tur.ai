"""Prompt construction for assistant interactions."""

from __future__ import annotations

from typing import Sequence

from tur.llm.base import ChatMessage
from tur.memory.models import MemoryEntry
from tur.personalities.models import PersonalityProfile


class PromptBuilder:
    """Builds the system prompt given personality and memory context."""

    def build(
        self,
        personality: PersonalityProfile,
        recalled_memories: Sequence[MemoryEntry],
        conversation: Sequence[ChatMessage],
    ) -> str:
        """Compose the active system prompt for the LLM."""
        memory_block = self._format_memories(recalled_memories)
        conversation_note = (
            "You are in an ongoing chat session. Maintain continuity with prior messages."
            if conversation
            else "This is the beginning of a chat session."
        )

        return "\n\n".join(
            [
                personality.system_prompt.strip(),
                f"Speaking style: {personality.speaking_style}",
                f"Humor level: {personality.humor_level}",
                f"Verbosity: {personality.verbosity}",
                conversation_note,
                memory_block,
            ]
        ).strip()

    def _format_memories(self, memories: Sequence[MemoryEntry]) -> str:
        if not memories:
            return "Relevant rider memory: none."

        formatted = "\n".join(f"- {memory.content}" for memory in memories)
        return f"Relevant rider memory:\n{formatted}"
