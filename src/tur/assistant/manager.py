"""Application service coordinating assistant behavior."""

from __future__ import annotations

from tur.assistant.prompt_builder import PromptBuilder
from tur.llm.base import ChatMessage, LLMClient
from tur.memory.base import MemoryStore
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
        default_personality: str = "karen",
    ) -> None:
        self._registry = personality_registry
        self._memory_store = memory_store
        self._llm_client = llm_client
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._history: list[ChatMessage] = []
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
        recalled_memories = self._memory_store.recall(user_message, limit=5)
        user_chat_message = ChatMessage(role="user", content=user_message)
        conversation = [*self._history, user_chat_message]
        system_prompt = self._prompt_builder.build(
            personality=self._active_personality,
            recalled_memories=recalled_memories,
            conversation=self._history,
        )
        reply = self._llm_client.generate_reply(system_prompt=system_prompt, messages=conversation)
        self._history.extend([user_chat_message, ChatMessage(role="assistant", content=reply)])
        return reply
