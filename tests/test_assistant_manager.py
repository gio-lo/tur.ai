from pathlib import Path

from tur.assistant.prompt_builder import PromptBuilder
from tur.assistant.manager import AssistantManager
from tur.llm.base import ChatMessage, LLMClient
from tur.memory.extractor import MemoryExtractor
from tur.memory.json_store import JSONMemoryStore
from tur.memory.models import MemoryEntry
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


def test_assistant_manager_auto_saves_selected_memories_across_personalities(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        llm_client=llm_client,
        memory_extractor=MemoryExtractor(),
        default_personality="nina",
    )

    manager.generate_reply("I ride a Ninja 400")
    manager.switch_personality("tom")
    manager.generate_reply("What bike do I ride?")

    memories = memory_store.list_memories()
    assert any(memory.content == "I ride a Ninja 400." for memory in memories)

    recalled = memory_store.recall("Ninja", personality_key="tom", personality_name="Tom")
    assert recalled[0].content == "I ride a Ninja 400."


def test_memory_extractor_handles_greeting_then_fact() -> None:
    extractor = MemoryExtractor()

    memory = extractor.extract("hey nina. im allergic to peanut butter.")

    assert memory == "im allergic to peanut butter."


def test_prompt_builder_requires_explicit_first_sentence_source_for_handoff_memory() -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    personality = registry.get("tom")
    builder = PromptBuilder()

    prompt = builder.build(
        personality=personality,
        recalled_memories=[
            MemoryEntry(
                content="im allergic to peanut butter.",
                created_at="2026-07-06T00:00:00+00:00",
                source_personality_name="Nina",
            )
        ],
        conversation=[],
        user_message="what am i allergic to?",
    )

    assert "explicitly say in your first sentence that Nina told you" in prompt
