"""Memory domain models."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True, frozen=True)
class MemoryEntry:
    """Represents one stored memory."""

    content: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        """Serialize the memory entry for persistence."""
        return asdict(self)
