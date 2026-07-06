"""Prompt construction for assistant interactions."""

from __future__ import annotations

import re
from typing import Sequence

from tur.environment.models import EnvironmentEvent, EnvironmentMode
from tur.environment.presence_models import PersonalityPresence
from tur.llm.base import ChatMessage
from tur.memory.models import MemoryEntry
from tur.personalities.models import PersonalityProfile


class PromptBuilder:
    """Builds the system prompt given personality and memory context."""

    def __init__(
        self,
        max_reference_sections: int = 1,
        fallback_reference_sections: int = 0,
        max_reference_characters: int = 600,
    ) -> None:
        self._max_reference_sections = max_reference_sections
        self._fallback_reference_sections = fallback_reference_sections
        self._max_reference_characters = max(0, max_reference_characters)

    def build(
        self,
        personality: PersonalityProfile,
        recalled_memories: Sequence[MemoryEntry],
        environment_events: Sequence[EnvironmentEvent],
        environment_mode: EnvironmentMode,
        active_presence: PersonalityPresence | None,
        other_presences: Sequence[PersonalityPresence],
        conversation: Sequence[ChatMessage],
        user_message: str,
    ) -> str:
        """Compose the active system prompt for the LLM."""
        memory_block = self._format_memories(recalled_memories)
        environment_block = self._format_environment(environment_events)
        mode_block = self._format_mode(environment_mode)
        presence_block = self._format_presence(personality, active_presence, other_presences)
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
                presence_block,
                mode_block,
                environment_block,
                conversation_note,
                memory_block,
            ]
        ).strip()

    def _format_memories(self, memories: Sequence[MemoryEntry]) -> str:
        if not memories:
            return "Relevant rider memory: none."

        formatted = "\n".join(self._format_memory_line(memory) for memory in memories)
        return f"Relevant rider memory:\n{formatted}"

    def _format_environment(self, events: Sequence[EnvironmentEvent]) -> str:
        if not events:
            return "Recent environment: none."

        formatted = "\n".join(f"- {event.summary}" for event in events)
        return (
            "Recent environment:\n"
            f"{formatted}\n"
            "Use only when relevant. Treat as ambient context, not shared-memory exposition."
        )

    def _format_mode(self, mode: EnvironmentMode) -> str:
        mode_rules = {
            "riding": "Current mode: riding. Be as brief as possible. Prioritize safety and low distraction.",
            "stopped": "Current mode: stopped. Stay brief, but you may add a little context if useful.",
            "parked": "Current mode: parked. You may show more personality, but still keep replies naturally concise.",
        }
        return mode_rules[mode]

    def _format_presence(
        self,
        personality: PersonalityProfile,
        active_presence: PersonalityPresence | None,
        other_presences: Sequence[PersonalityPresence],
    ) -> str:
        lines = [
            "Presence:",
            "- You are an ongoing presence around Gio.",
        ]
        if personality.hobbies:
            hobbies = ", ".join(personality.hobbies[:2])
            lines.append(f"- Interests: {hobbies}.")
        if personality.ambient_style:
            lines.append(f"- Vibe: {personality.ambient_style}.")
        if active_presence and active_presence.current_activity:
            lines.append(f"- Current background activity: {active_presence.current_activity}.")
        elif personality.default_activity:
            lines.append(f"- Current background activity: {personality.default_activity}.")

        if other_presences:
            for presence in other_presences[:1]:
                detail = presence.current_activity or presence.current_focus
                if detail:
                    lines.append(
                        f"- {presence.personality_name} recently seemed occupied with {detail}."
                    )

        lines.append(
            "- Reference these lightly. Do not let them make your reply longer."
        )
        return "\n".join(lines)

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
                f"[Reference: {reference.name}]\n{self._clip_reference(reference.content)}"
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

    def _clip_reference(self, content: str) -> str:
        if self._max_reference_characters <= 0 or len(content) <= self._max_reference_characters:
            return content

        return f"{content[: self._max_reference_characters].rstrip()}..."

    def _format_memory_line(self, memory: MemoryEntry) -> str:
        if memory.source_personality_name:
            return (
                f"- {memory.content} "
                f"(Source: {memory.source_personality_name}. "
                "If you use this memory in your reply, explicitly say in your first sentence "
                f"that {memory.source_personality_name} told you.)"
            )

        return f"- {memory.content}"
