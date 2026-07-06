"""JSON-backed store for per-personality presence state."""

from __future__ import annotations

import json
from pathlib import Path

from tur.environment.presence_models import PersonalityPresence


class JSONPersonalityPresenceStore:
    """Caches lightweight ongoing state for personalities."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._cache: dict[str, PersonalityPresence] | None = None
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, personality_key: str) -> PersonalityPresence | None:
        """Return one stored presence entry."""
        return self._load().get(personality_key)

    def list(self) -> list[PersonalityPresence]:
        """Return all known presence entries."""
        return list(self._load().values())

    def upsert(self, presence: PersonalityPresence) -> PersonalityPresence:
        """Insert or replace a presence entry."""
        payload = self._load()
        payload[presence.personality_key] = presence
        self._save(payload)
        return presence

    def _load(self) -> dict[str, PersonalityPresence]:
        if self._cache is not None:
            return dict(self._cache)

        if not self._path.exists():
            self._cache = {}
            return {}

        raw_items = json.loads(self._path.read_text(encoding="utf-8"))
        self._cache = {
            item["personality_key"]: PersonalityPresence(**item)
            for item in raw_items
        }
        return dict(self._cache)

    def _save(self, presence_map: dict[str, PersonalityPresence]) -> None:
        payload = [presence.to_dict() for presence in presence_map.values()]
        self._cache = dict(presence_map)
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
