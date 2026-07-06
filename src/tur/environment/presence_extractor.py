"""Heuristics for ongoing personality focus and activity."""

from __future__ import annotations

from datetime import UTC, datetime

from tur.environment.extractor import EnvironmentExtractor
from tur.environment.presence_models import PersonalityPresence
from tur.personalities.models import PersonalityProfile


class PresenceExtractor:
    """Builds lightweight persistent presence state from interactions."""

    def __init__(self) -> None:
        self._environment_extractor = EnvironmentExtractor()

    def update_presence(
        self,
        profile: PersonalityProfile,
        user_message: str,
        assistant_reply: str,
        previous: PersonalityPresence | None = None,
    ) -> PersonalityPresence:
        """Create the next presence snapshot for a personality."""
        topic = self._environment_extractor._topic_for_text(f"{user_message} {assistant_reply}")  # noqa: SLF001
        current_focus = topic or (previous.current_focus if previous else None)
        current_activity = self._activity_for(profile, current_focus)

        return PersonalityPresence(
            personality_key=profile.key,
            personality_name=profile.name,
            current_focus=current_focus,
            current_activity=current_activity,
            last_updated_at=datetime.now(UTC).isoformat(),
        )

    def _activity_for(self, profile: PersonalityProfile, current_focus: str | None) -> str | None:
        if current_focus:
            return f"currently preoccupied with {current_focus}"
        if profile.default_activity:
            return profile.default_activity
        if profile.hobbies:
            return f"drifting between {profile.hobbies[0]}"
        return None
