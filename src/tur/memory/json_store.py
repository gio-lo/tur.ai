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
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def remember(self, content: str) -> MemoryEntry:
        """Append a new memory entry to the JSON file."""
        entry = MemoryEntry(
            content=content.strip(),
            created_at=datetime.now(UTC).isoformat(),
        )
        memories = self._load()
        memories.append(entry)
        self._save(memories)
        return entry

    def recall(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Return memory entries that match the query with a simple score."""
        query_terms = {term.lower() for term in query.split() if term.strip()}
        if not query_terms:
            return self.list_memories()[-limit:]

        scored: list[tuple[int, MemoryEntry]] = []
        for entry in self._load():
            content_terms = set(entry.content.lower().split())
            score = len(query_terms & content_terms)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
        return [entry for _, entry in scored[:limit]]

    def list_memories(self) -> list[MemoryEntry]:
        """Return all saved memory entries."""
        return self._load()

    def _load(self) -> list[MemoryEntry]:
        if not self._path.exists():
            return []

        raw_items = json.loads(self._path.read_text(encoding="utf-8"))
        return [MemoryEntry(**item) for item in raw_items]

    def _save(self, memories: list[MemoryEntry]) -> None:
        payload = [memory.to_dict() for memory in memories]
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
