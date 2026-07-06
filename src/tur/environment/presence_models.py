"""Persistent per-personality presence state."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True, frozen=True)
class PersonalityPresence:
    """Lightweight ongoing state for one assistant personality."""

    personality_key: str
    personality_name: str
    current_focus: str | None = None
    current_activity: str | None = None
    last_updated_at: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Serialize the presence state for persistence."""
        return asdict(self)
