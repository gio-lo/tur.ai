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
    from tur.assistant.prompt_builder import PromptBuilder

    return AssistantManager(
        personality_registry=personality_registry,
        memory_store=memory_store,
        llm_client=llm_client,
        prompt_builder=PromptBuilder(
            max_reference_sections=settings.max_personality_references,
            fallback_reference_sections=settings.fallback_personality_references,
            max_reference_characters=settings.max_reference_characters,
        ),
        default_personality=settings.default_personality,
        max_history_messages=settings.max_history_messages,
    )


def main() -> None:
    """Run the terminal application."""
    manager = build_application()
    run_terminal_chat(manager)


if __name__ == "__main__":
    main()
