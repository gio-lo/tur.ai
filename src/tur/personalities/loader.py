"""Personality loading utilities."""

from __future__ import annotations

from pathlib import Path

import yaml

from tur.personalities.models import PersonalityProfile


class PersonalityRegistry:
    """Loads and serves available assistant personalities."""

    def __init__(self, personalities: dict[str, PersonalityProfile]) -> None:
        self._personalities = personalities

    @classmethod
    def from_directory(cls, directory: Path) -> "PersonalityRegistry":
        """Load all YAML personalities from a directory."""
        if not directory.exists():
            raise FileNotFoundError(f"Personality directory not found: {directory}")

        personalities: dict[str, PersonalityProfile] = {}
        for path in sorted(directory.glob("*.yaml")):
            key = path.stem
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            personalities[key] = PersonalityProfile.from_dict(key, payload)

        if not personalities:
            raise ValueError(f"No personality files found in {directory}")

        return cls(personalities)

    def get(self, key: str) -> PersonalityProfile:
        """Return a personality by key."""
        try:
            return self._personalities[key]
        except KeyError as exc:
            available = ", ".join(sorted(self._personalities))
            raise KeyError(f"Unknown personality '{key}'. Available: {available}") from exc

    def keys(self) -> list[str]:
        """Return available personality keys."""
        return sorted(self._personalities)
