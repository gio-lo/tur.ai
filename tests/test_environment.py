from pathlib import Path

from tur.environment.extractor import EnvironmentExtractor
from tur.environment.json_store import JSONEnvironmentStore


def test_environment_store_records_and_returns_recent_events(tmp_path: Path) -> None:
    store = JSONEnvironmentStore(tmp_path / "environment.json")
    store.record_event("Tom was recently talking with Gio about food allergies.")
    store.record_event("Nina was recently talking with Gio about motorcycles.")

    recent = store.recent_events(limit=1)

    assert len(recent) == 1
    assert recent[0].summary == "Nina was recently talking with Gio about motorcycles."


def test_environment_extractor_summarizes_allergy_topics() -> None:
    extractor = EnvironmentExtractor()

    summary = extractor.summarize_interaction(
        personality_name="Tom",
        user_message="should I eat this peanut butter jelly sandwich?",
        assistant_reply="Given your peanut allergy, no.",
    )

    assert summary == "Tom was recently talking with Gio about food allergies and what to avoid."


def test_environment_store_persists_mode(tmp_path: Path) -> None:
    store = JSONEnvironmentStore(tmp_path / "environment.json")

    store.set_mode("riding")

    assert store.get_mode() == "riding"
