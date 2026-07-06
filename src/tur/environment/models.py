"""Environment domain models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


EnvironmentMode = Literal["riding", "stopped", "parked"]


@dataclass(slots=True, frozen=True)
class EnvironmentEvent:
    """Represents one recent world-state event around Gio."""

    summary: str
    created_at: str
    source_personality_key: str | None = None
    source_personality_name: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Serialize the environment event for persistence."""
        return asdict(self)
