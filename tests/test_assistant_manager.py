from pathlib import Path

from tur.assistant.prompt_builder import PromptBuilder
from tur.assistant.manager import AssistantManager
from tur.llm.base import ChatMessage, LLMClient
from tur.memory.json_store import JSONMemoryStore
from tur.personalities.loader import PersonalityRegistry


PERSONALITY_DIR = Path(__file__).resolve().parents[1] / "src" / "tur" / "personalities"


class StubLLMClient(LLMClient):
    def __init__(self) -> None:
        self.message_counts: list[int] = []

    def generate_reply(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        assert "Relevant rider memory" in system_prompt
        assert "Personality references:" in system_prompt
        self.message_counts.append(len(messages))
        return f"stub reply to: {messages[-1].content}"

    def stream_reply(self, system_prompt: str, messages: list[ChatMessage]):
        self.message_counts.append(len(messages))
        yield f"stub reply to: {messages[-1].content}"


def test_assistant_manager_uses_memory_and_llm(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    memory_store.remember("The rider owns a Ninja 400.")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        llm_client=llm_client,
        default_personality="nina",
    )

    reply = manager.generate_reply("Tell me what you know about my bike.")

    assert reply == "stub reply to: Tell me what you know about my bike."
    assert llm_client.message_counts == [1]


def test_assistant_manager_caps_history_and_streams(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        llm_client=llm_client,
        prompt_builder=PromptBuilder(max_reference_sections=1),
        default_personality="nina",
        max_history_messages=2,
    )

    manager.generate_reply("first")
    manager.generate_reply("second")
    streamed = "".join(manager.stream_reply("third"))

    assert streamed == "stub reply to: third"
    assert llm_client.message_counts == [1, 3, 3]


def test_prompt_builder_can_skip_irrelevant_reference_fallback(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    personality = registry.get("nina")
    builder = PromptBuilder(max_reference_sections=1, fallback_reference_sections=0)

    prompt = builder.build(
        personality=personality,
        recalled_memories=[],
        conversation=[],
        user_message="hello",
    )

    assert "Personality references: none." in prompt
