"""Application entrypoint for the terminal assistant."""

from __future__ import annotations

from tur.assistant.manager import AssistantManager
from tur.config.settings import AppSettings
from tur.llm.factory import build_llm_client
from tur.memory.json_store import JSONMemoryStore
from tur.personalities.loader import PersonalityRegistry
from tur.services.terminal_chat import run_terminal_chat


def build_application() -> AssistantManager:
    """Construct the assistant manager and its dependencies."""
    settings = AppSettings.load()
    personality_registry = PersonalityRegistry.from_directory(settings.personality_dir)
    memory_store = JSONMemoryStore(settings.memory_file)
    llm_client = build_llm_client(settings)

    return AssistantManager(
        personality_registry=personality_registry,
        memory_store=memory_store,
        llm_client=llm_client,
        default_personality=settings.default_personality,
    )


def main() -> None:
    """Run the terminal application."""
    manager = build_application()
    run_terminal_chat(manager)


if __name__ == "__main__":
    main()
