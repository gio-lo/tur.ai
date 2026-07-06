from pathlib import Path

import pytest

from tur.personalities.loader import PersonalityRegistry


def test_personality_registry_loads_yaml_profiles() -> None:
    registry = PersonalityRegistry.from_directory(Path("src/tur/personalities"))

    assert {"karen", "tom", "tito", "asuka"}.issubset(set(registry.keys()))
    assert registry.get("karen").name == "Karen"


def test_personality_registry_rejects_unknown_profile() -> None:
    registry = PersonalityRegistry.from_directory(Path("src/tur/personalities"))

    with pytest.raises(KeyError):
        registry.get("unknown")
