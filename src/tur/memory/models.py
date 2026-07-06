"""Memory domain models."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True, frozen=True)
class MemoryEntry:
    """Represents one stored memory."""

    content: str
    created_at: str
    source_personality_key: str | None = None
    source_personality_name: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Serialize the memory entry for persistence."""
        return asdict(self)
