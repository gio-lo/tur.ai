"""JSON-backed memory store."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path

from tur.memory.base import MemoryStore
from tur.memory.models import MemoryEntry


class JSONMemoryStore(MemoryStore):
    """Simple JSON implementation for Sprint 0."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._cache: list[MemoryEntry] | None = None
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def remember(
        self,
        content: str,
        source_personality_key: str | None = None,
        source_personality_name: str | None = None,
    ) -> MemoryEntry:
        """Append a new memory entry to the JSON file."""
        normalized_content = content.strip()
        existing = self._find_by_content(normalized_content)
        if existing is not None:
            return existing

        entry = MemoryEntry(
            content=normalized_content,
            created_at=datetime.now(UTC).isoformat(),
            source_personality_key=source_personality_key,
            source_personality_name=source_personality_name,
        )
        memories = self._load()
        memories.append(entry)
        self._save(memories)
        return entry

    def recall(
        self,
        query: str,
        limit: int = 5,
        personality_key: str | None = None,
        personality_name: str | None = None,
    ) -> list[MemoryEntry]:
        """Return memory entries that match the query with a simple score."""
        query_terms = {term.lower() for term in query.split() if term.strip()}
        if not query_terms:
            memories = self.list_memories()[-limit:]
            return self._decorate_recalls(memories, personality_key, personality_name)

        scored: list[tuple[int, MemoryEntry]] = []
        for entry in self._load():
            content_terms = set(entry.content.lower().split())
            score = len(query_terms & content_terms)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
        memories = [entry for _, entry in scored[:limit]]
        return self._decorate_recalls(memories, personality_key, personality_name)

    def list_memories(self) -> list[MemoryEntry]:
        """Return all saved memory entries."""
        return self._load()

    def _load(self) -> list[MemoryEntry]:
        if self._cache is not None:
            return list(self._cache)

        if not self._path.exists():
            self._cache = []
            return []

        raw_items = json.loads(self._path.read_text(encoding="utf-8"))
        self._cache = [MemoryEntry(**item) for item in raw_items]
        return list(self._cache)

    def _save(self, memories: list[MemoryEntry]) -> None:
        payload = [memory.to_dict() for memory in memories]
        self._cache = list(memories)
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _find_by_content(self, content: str) -> MemoryEntry | None:
        for memory in self._load():
            if memory.content == content:
                return memory
        return None

    def _decorate_recalls(
        self,
        memories: list[MemoryEntry],
        personality_key: str | None,
        personality_name: str | None,
    ) -> list[MemoryEntry]:
        if not personality_key or not personality_name:
            return memories

        updated_memories = self._load()
        changed = False
        recalled: list[MemoryEntry] = []

        for memory in memories:
            if memory.source_personality_key and memory.source_personality_key != personality_key:
                source_name = memory.source_personality_name or memory.source_personality_key
                recalled.append(
                    MemoryEntry(
                        content=memory.content,
                        created_at=memory.created_at,
                        source_personality_key=memory.source_personality_key,
                        source_personality_name=source_name,
                    )
                )

                for index, stored_memory in enumerate(updated_memories):
                    if stored_memory.created_at == memory.created_at and stored_memory.content == memory.content:
                        updated_memories[index] = MemoryEntry(
                            content=stored_memory.content,
                            created_at=stored_memory.created_at,
                        )
                        changed = True
                        break
                continue

            recalled.append(memory)

        if changed:
            self._save(updated_memories)

        return recalled
