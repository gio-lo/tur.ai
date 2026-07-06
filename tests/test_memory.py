from pathlib import Path

from tur.memory.json_store import JSONMemoryStore


def test_remember_and_list_memories(tmp_path: Path) -> None:
    store = JSONMemoryStore(tmp_path / "memory.json")

    store.remember("I own a Ninja 400.")
    store.remember("I prefer short rides after work.")

    memories = store.list_memories()

    assert [memory.content for memory in memories] == [
        "I own a Ninja 400.",
        "I prefer short rides after work.",
    ]


def test_recall_matches_query_terms(tmp_path: Path) -> None:
    store = JSONMemoryStore(tmp_path / "memory.json")
    store.remember("My motorcycle is a Kawasaki Ninja 400.")
    store.remember("I wear earplugs on highway rides.")

    recalled = store.recall("Ninja highway", limit=5)

    assert len(recalled) == 2
    assert recalled[0].content in {
        "My motorcycle is a Kawasaki Ninja 400.",
        "I wear earplugs on highway rides.",
    }


def test_cross_personality_recall_mentions_source_once(tmp_path: Path) -> None:
    store = JSONMemoryStore(tmp_path / "memory.json")
    store.remember(
        "I ride a Ninja 400.",
        source_personality_key="nina",
        source_personality_name="Nina",
    )

    recalled_by_tom = store.recall(
        "Ninja",
        personality_key="tom",
        personality_name="Tom",
    )

    assert recalled_by_tom[0].content == "I ride a Ninja 400."
    assert recalled_by_tom[0].source_personality_name == "Nina"

    recalled_again = store.recall(
        "Ninja",
        personality_key="tom",
        personality_name="Tom",
    )
    assert recalled_again[0].content == "I ride a Ninja 400."
    assert recalled_again[0].source_personality_name is None
