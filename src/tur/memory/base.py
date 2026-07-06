"""Memory storage interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tur.memory.models import MemoryEntry


class MemoryStore(ABC):
    """Abstract memory persistence contract."""

    @abstractmethod
    def remember(
        self,
        content: str,
        source_personality_key: str | None = None,
        source_personality_name: str | None = None,
    ) -> MemoryEntry:
        """Persist a new memory entry."""

    @abstractmethod
    def recall(
        self,
        query: str,
        limit: int = 5,
        personality_key: str | None = None,
        personality_name: str | None = None,
    ) -> list[MemoryEntry]:
        """Find memory entries relevant to the query."""

    @abstractmethod
    def list_memories(self) -> list[MemoryEntry]:
        """Return all stored memory entries."""
