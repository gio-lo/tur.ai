"""JSON-backed environment store."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path

from tur.environment.base import EnvironmentStore
from tur.environment.models import EnvironmentEvent


class JSONEnvironmentStore(EnvironmentStore):
    """Simple JSON environment implementation with in-process caching."""

    def __init__(self, path: Path, max_events: int = 50) -> None:
        self._path = path
        self._max_events = max(1, max_events)
        self._cache: list[EnvironmentEvent] | None = None
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record_event(
        self,
        summary: str,
        source_personality_key: str | None = None,
        source_personality_name: str | None = None,
    ) -> EnvironmentEvent:
        """Append a new environment event to the JSON file."""
        normalized_summary = " ".join(summary.strip().split())
        if not normalized_summary:
            raise ValueError("Environment event summary cannot be empty.")

        recent = self.recent_events(limit=1)
        if recent and recent[0].summary == normalized_summary:
            return recent[0]

        event = EnvironmentEvent(
            summary=normalized_summary,
            created_at=datetime.now(UTC).isoformat(),
            source_personality_key=source_personality_key,
            source_personality_name=source_personality_name,
        )
        events = self._load()
        events.append(event)
        self._save(events[-self._max_events :])
        return event

    def recent_events(self, limit: int = 5) -> list[EnvironmentEvent]:
        """Return the most recent environment events."""
        if limit <= 0:
            return []
        return self._load()[-limit:]

    def list_events(self) -> list[EnvironmentEvent]:
        """Return all saved environment events."""
        return self._load()

    def _load(self) -> list[EnvironmentEvent]:
        if self._cache is not None:
            return list(self._cache)

        if not self._path.exists():
            self._cache = []
            return []

        raw_items = json.loads(self._path.read_text(encoding="utf-8"))
        self._cache = [EnvironmentEvent(**item) for item in raw_items]
        return list(self._cache)

    def _save(self, events: list[EnvironmentEvent]) -> None:
        payload = [event.to_dict() for event in events]
        self._cache = list(events)
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
