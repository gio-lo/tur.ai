"""Prompt construction for assistant interactions."""

from __future__ import annotations

import re
from typing import Sequence

from tur.llm.base import ChatMessage
from tur.memory.models import MemoryEntry
from tur.personalities.models import PersonalityProfile


class PromptBuilder:
    """Builds the system prompt given personality and memory context."""

    def __init__(
        self,
        max_reference_sections: int = 2,
        fallback_reference_sections: int = 1,
    ) -> None:
        self._max_reference_sections = max_reference_sections
        self._fallback_reference_sections = fallback_reference_sections

    def build(
        self,
        personality: PersonalityProfile,
        recalled_memories: Sequence[MemoryEntry],
        conversation: Sequence[ChatMessage],
        user_message: str,
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
                self._format_references(personality, user_message, conversation),
                conversation_note,
                memory_block,
            ]
        ).strip()

    def _format_memories(self, memories: Sequence[MemoryEntry]) -> str:
        if not memories:
            return "Relevant rider memory: none."

        formatted = "\n".join(f"- {memory.content}" for memory in memories)
        return f"Relevant rider memory:\n{formatted}"

    def _format_references(
        self,
        personality: PersonalityProfile,
        user_message: str,
        conversation: Sequence[ChatMessage],
    ) -> str:
        selected_references = self._select_references(personality, user_message, conversation)
        if not selected_references:
            return "Personality references: none."

        sections = "\n\n".join(
            [
                f"[Reference: {reference.name}]\n{reference.content}"
                for reference in selected_references
            ]
        )
        return f"Personality references:\n{sections}"

    def _select_references(
        self,
        personality: PersonalityProfile,
        user_message: str,
        conversation: Sequence[ChatMessage],
    ) -> Sequence:
        if not personality.references or self._max_reference_sections <= 0:
            return ()

        query_terms = self._tokenize(
            " ".join([user_message, *(message.content for message in conversation[-2:])])
        )
        scored_references = []
        for index, reference in enumerate(personality.references):
            reference_terms = self._tokenize(f"{reference.name} {reference.content}")
            overlap = len(query_terms & reference_terms)
            scored_references.append((overlap, -index, reference))

        relevant_references = [item[2] for item in scored_references if item[0] > 0]
        if relevant_references:
            return relevant_references[: self._max_reference_sections]

        return personality.references[: min(self._fallback_reference_sections, len(personality.references))]

    def _tokenize(self, text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}
