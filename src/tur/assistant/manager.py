"""Application service coordinating assistant behavior."""

from __future__ import annotations

from typing import Iterator

from tur.assistant.prompt_builder import PromptBuilder
from tur.llm.base import ChatMessage, LLMClient
from tur.memory.base import MemoryStore
from tur.memory.extractor import MemoryExtractor
from tur.memory.models import MemoryEntry
from tur.personalities.loader import PersonalityRegistry
from tur.personalities.models import PersonalityProfile


class AssistantManager:
    """Coordinates personality, memory, prompts, and LLM access."""

    def __init__(
        self,
        personality_registry: PersonalityRegistry,
        memory_store: MemoryStore,
        llm_client: LLMClient,
        prompt_builder: PromptBuilder | None = None,
        default_personality: str = "nina",
        max_history_messages: int = 8,
        memory_extractor: MemoryExtractor | None = None,
    ) -> None:
        self._registry = personality_registry
        self._memory_store = memory_store
        self._llm_client = llm_client
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._memory_extractor = memory_extractor or MemoryExtractor()
        self._history: list[ChatMessage] = []
        self._max_history_messages = max(0, max_history_messages)
        self._active_personality = self._registry.get(default_personality)

    @property
    def active_personality(self) -> PersonalityProfile:
        """Return the current personality."""
        return self._active_personality

    def available_personalities(self) -> list[str]:
        """Return the available personality keys."""
        return self._registry.keys()

    def switch_personality(self, key: str) -> PersonalityProfile:
        """Switch the active assistant personality."""
        self._active_personality = self._registry.get(key)
        return self._active_personality

    def remember(self, content: str) -> MemoryEntry:
        """Store a memory entry through the abstract memory interface."""
        return self._memory_store.remember(content)

    def list_memories(self) -> list[MemoryEntry]:
        """Expose stored memories without leaking storage details."""
        return self._memory_store.list_memories()

    def generate_reply(self, user_message: str) -> str:
        """Generate a reply for the current conversation turn."""
        system_prompt, conversation, user_chat_message = self._build_turn_context(user_message)
        reply = self._llm_client.generate_reply(system_prompt=system_prompt, messages=conversation)
        self._record_turn(user_chat_message, reply)
        return reply

    def stream_reply(self, user_message: str) -> Iterator[str]:
        """Stream a reply for the current conversation turn."""
        system_prompt, conversation, user_chat_message = self._build_turn_context(user_message)
        chunks: list[str] = []
        for chunk in self._llm_client.stream_reply(system_prompt=system_prompt, messages=conversation):
            chunks.append(chunk)
            yield chunk

        reply = "".join(chunks).strip() or "I don't have a response yet."
        self._record_turn(user_chat_message, reply)

    def _build_turn_context(self, user_message: str) -> tuple[str, list[ChatMessage], ChatMessage]:
        self._remember_from_message(user_message)
        recalled_memories = self._memory_store.recall(
            user_message,
            limit=5,
            personality_key=self._active_personality.key,
            personality_name=self._active_personality.name,
        )
        history = self._recent_history()
        user_chat_message = ChatMessage(role="user", content=user_message)
        conversation = [*history, user_chat_message]
        system_prompt = self._prompt_builder.build(
            personality=self._active_personality,
            recalled_memories=recalled_memories,
            conversation=history,
            user_message=user_message,
        )
        return system_prompt, conversation, user_chat_message

    def _remember_from_message(self, user_message: str) -> None:
        extracted_memory = self._memory_extractor.extract(user_message)
        if extracted_memory is None:
            return

        self._memory_store.remember(
            extracted_memory,
            source_personality_key=self._active_personality.key,
            source_personality_name=self._active_personality.name,
        )

    def _recent_history(self) -> list[ChatMessage]:
        if self._max_history_messages <= 0:
            return []

        return self._history[-self._max_history_messages :]

    def _record_turn(self, user_message: ChatMessage, reply: str) -> None:
        self._history.extend([user_message, ChatMessage(role="assistant", content=reply)])
        if self._max_history_messages > 0:
            self._history = self._history[-self._max_history_messages :]
        else:
            self._history = []
