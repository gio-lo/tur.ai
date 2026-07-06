from pathlib import Path

import pytest

from tur.personalities.loader import PersonalityRegistry


def test_personality_registry_loads_directory_profiles() -> None:
    registry = PersonalityRegistry.from_directory(Path("src/tur/personalities"))

    assert {"nina", "tom", "tito", "asuka"}.issubset(set(registry.keys()))
    nina = registry.get("nina")
    assert nina.name == "Nina"
    assert any(reference.name.endswith(".md") for reference in nina.references)


def test_personality_registry_rejects_unknown_profile() -> None:
    registry = PersonalityRegistry.from_directory(Path("src/tur/personalities"))

    with pytest.raises(KeyError):
        registry.get("unknown")
