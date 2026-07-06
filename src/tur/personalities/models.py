"""Personality domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PersonalityReference:
    """Supplemental text file loaded into a personality's prompt context."""

    name: str
    content: str


@dataclass(slots=True, frozen=True)
class PersonalityProfile:
    """Configuration for one assistant personality."""

    key: str
    name: str
    description: str
    system_prompt: str
    wake_phrase: str
    sleep_phrase: str
    speaking_style: str
    humor_level: str
    verbosity: str
    hobbies: tuple[str, ...] = ()
    default_activity: str | None = None
    ambient_style: str | None = None
    references: tuple[PersonalityReference, ...] = ()

    @classmethod
    def from_dict(
        cls,
        key: str,
        data: dict[str, str],
        references: tuple[PersonalityReference, ...] = (),
    ) -> "PersonalityProfile":
        """Create a profile from YAML-loaded data."""
        required_fields = {
            "name",
            "description",
            "system_prompt",
            "wake_phrase",
            "sleep_phrase",
            "speaking_style",
            "humor_level",
            "verbosity",
        }
        missing = sorted(required_fields - data.keys())
        if missing:
            raise ValueError(f"Personality '{key}' is missing required fields: {', '.join(missing)}")

        return cls(
            key=key,
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            wake_phrase=data["wake_phrase"],
            sleep_phrase=data["sleep_phrase"],
            speaking_style=data["speaking_style"],
            humor_level=data["humor_level"],
            verbosity=data["verbosity"],
            hobbies=tuple(data.get("hobbies", [])),
            default_activity=data.get("default_activity"),
            ambient_style=data.get("ambient_style"),
            references=references,
        )
