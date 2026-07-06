from pathlib import Path

from tur.assistant.manager import AssistantManager
from tur.llm.base import ChatMessage, LLMClient
from tur.memory.json_store import JSONMemoryStore
from tur.personalities.loader import PersonalityRegistry


PERSONALITY_DIR = Path(__file__).resolve().parents[1] / "src" / "tur" / "personalities"


class StubLLMClient(LLMClient):
    def generate_reply(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        assert "Relevant rider memory" in system_prompt
        assert "Personality references:" in system_prompt
        return f"stub reply to: {messages[-1].content}"


def test_assistant_manager_uses_memory_and_llm(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    memory_store.remember("The rider owns a Ninja 400.")

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        llm_client=StubLLMClient(),
        default_personality="nina",
    )

    reply = manager.generate_reply("Tell me what you know about my bike.")

    assert reply == "stub reply to: Tell me what you know about my bike."
