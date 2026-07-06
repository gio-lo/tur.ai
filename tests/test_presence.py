from pathlib import Path

from tur.environment.presence_extractor import PresenceExtractor
from tur.environment.presence_models import PersonalityPresence
from tur.environment.presence_store import JSONPersonalityPresenceStore
from tur.personalities.loader import PersonalityRegistry


PERSONALITY_DIR = Path(__file__).resolve().parents[1] / "src" / "tur" / "personalities"


def test_presence_store_persists_entries(tmp_path: Path) -> None:
    store = JSONPersonalityPresenceStore(tmp_path / "presence.json")

    store.upsert(
        PersonalityPresence(
            personality_key="nina",
            personality_name="Nina",
            current_focus="food allergies and what to avoid",
            current_activity="currently preoccupied with food allergies and what to avoid",
        )
    )

    entry = store.get("nina")
    assert entry is not None
    assert entry.current_focus == "food allergies and what to avoid"


def test_presence_extractor_uses_profile_defaults() -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    nina = registry.get("nina")
    extractor = PresenceExtractor()

    presence = extractor.update_presence(
        profile=nina,
        user_message="hello",
        assistant_reply="Hi.",
        previous=None,
    )

    assert presence.current_activity == "quietly keeping an eye on Gio's routines and comfort"
