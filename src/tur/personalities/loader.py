"""Personality loading utilities."""

from __future__ import annotations

from pathlib import Path

import yaml

from tur.personalities.models import PersonalityProfile


class PersonalityRegistry:
    """Loads and serves available assistant personalities."""

    PROFILE_FILE_NAME = "profile.yaml"

    def __init__(self, personalities: dict[str, PersonalityProfile]) -> None:
        self._personalities = personalities

    @classmethod
    def from_directory(cls, directory: Path) -> "PersonalityRegistry":
        """Load all personalities from child directories."""
        if not directory.exists():
            raise FileNotFoundError(f"Personality directory not found: {directory}")

        personalities: dict[str, PersonalityProfile] = {}
        for path in sorted(directory.iterdir()):
            if not path.is_dir():
                continue

            profile_path = path / cls.PROFILE_FILE_NAME
            if not profile_path.exists():
                continue

            key = path.name
            payload = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            references = cls._load_references(path, profile_path)
            personalities[key] = PersonalityProfile.from_dict(key, payload, references=references)

        if not personalities:
            raise ValueError(f"No personality directories found in {directory}")

        return cls(personalities)

    @staticmethod
    def _load_references(
        personality_directory: Path,
        profile_path: Path,
    ) -> tuple["PersonalityReference", ...]:
        """Load all non-profile text files in a personality directory as references."""
        from tur.personalities.models import PersonalityReference

        references: list[PersonalityReference] = []
        for path in sorted(personality_directory.rglob("*")):
            if not path.is_file() or path == profile_path:
                continue

            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            references.append(
                PersonalityReference(
                    name=path.relative_to(personality_directory).as_posix(),
                    content=content,
                )
            )

        return tuple(references)

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
