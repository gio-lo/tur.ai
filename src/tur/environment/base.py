"""Environment storage interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tur.environment.models import EnvironmentEvent, EnvironmentMode


class EnvironmentStore(ABC):
    """Abstract environment persistence contract."""

    @abstractmethod
    def record_event(
        self,
        summary: str,
        source_personality_key: str | None = None,
        source_personality_name: str | None = None,
    ) -> EnvironmentEvent:
        """Persist a new environment event."""

    @abstractmethod
    def recent_events(self, limit: int = 5) -> list[EnvironmentEvent]:
        """Return the most recent environment events."""

    @abstractmethod
    def list_events(self) -> list[EnvironmentEvent]:
        """Return all persisted environment events."""

    @abstractmethod
    def set_mode(self, mode: EnvironmentMode) -> EnvironmentMode:
        """Persist the current environment mode."""

    @abstractmethod
    def get_mode(self) -> EnvironmentMode:
        """Return the current environment mode."""
