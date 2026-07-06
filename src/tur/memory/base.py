"""Memory storage interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tur.memory.models import MemoryEntry


class MemoryStore(ABC):
    """Abstract memory persistence contract."""

    @abstractmethod
    def remember(self, content: str) -> MemoryEntry:
        """Persist a new memory entry."""

    @abstractmethod
    def recall(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Find memory entries relevant to the query."""

    @abstractmethod
    def list_memories(self) -> list[MemoryEntry]:
        """Return all stored memory entries."""
