from pathlib import Path

from tur.assistant.prompt_builder import PromptBuilder
from tur.assistant.manager import AssistantManager
from tur.environment.json_store import JSONEnvironmentStore
from tur.environment.presence_store import JSONPersonalityPresenceStore
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
        assert "Presence:" in system_prompt
        assert "Recent environment:" in system_prompt
        assert "Current mode:" in system_prompt
        self.message_counts.append(len(messages))
        return f"stub reply to: {messages[-1].content}"

    def stream_reply(self, system_prompt: str, messages: list[ChatMessage]):
        assert "Presence:" in system_prompt
        self.message_counts.append(len(messages))
        yield f"stub reply to: {messages[-1].content}"


def test_assistant_manager_uses_memory_and_llm(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    environment_store = JSONEnvironmentStore(tmp_path / "environment.json")
    presence_store = JSONPersonalityPresenceStore(tmp_path / "presence.json")
    memory_store.remember("The rider owns a Ninja 400.")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        environment_store=environment_store,
        presence_store=presence_store,
        llm_client=llm_client,
        default_personality="nina",
    )

    reply = manager.generate_reply("Tell me what you know about my bike.")

    assert reply == "stub reply to: Tell me what you know about my bike."
    assert llm_client.message_counts == [1]


def test_assistant_manager_caps_history_and_streams(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    environment_store = JSONEnvironmentStore(tmp_path / "environment.json")
    presence_store = JSONPersonalityPresenceStore(tmp_path / "presence.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        environment_store=environment_store,
        presence_store=presence_store,
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
        environment_events=[],
        environment_mode="parked",
        active_presence=None,
        other_presences=[],
        conversation=[],
        user_message="hello",
    )

    assert "Personality references: none." in prompt


def test_assistant_manager_auto_saves_selected_memories_across_personalities(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    environment_store = JSONEnvironmentStore(tmp_path / "environment.json")
    presence_store = JSONPersonalityPresenceStore(tmp_path / "presence.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        environment_store=environment_store,
        presence_store=presence_store,
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
        environment_events=[],
        environment_mode="parked",
        active_presence=None,
        other_presences=[],
        conversation=[],
        user_message="what am i allergic to?",
    )

    assert "explicitly say in your first sentence that Nina told you" in prompt


def test_assistant_manager_records_recent_environment_events(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    environment_store = JSONEnvironmentStore(tmp_path / "environment.json")
    presence_store = JSONPersonalityPresenceStore(tmp_path / "presence.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        environment_store=environment_store,
        presence_store=presence_store,
        llm_client=llm_client,
        default_personality="tom",
        max_environment_events=3,
    )

    manager.generate_reply("should I eat this peanut butter jelly sandwich?")

    events = environment_store.recent_events(limit=1)
    assert events[0].summary == "Tom was recently talking with Gio about food and snack safety."


def test_assistant_manager_updates_personality_presence_state(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    environment_store = JSONEnvironmentStore(tmp_path / "environment.json")
    presence_store = JSONPersonalityPresenceStore(tmp_path / "presence.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        environment_store=environment_store,
        presence_store=presence_store,
        llm_client=llm_client,
        default_personality="tom",
    )

    manager.generate_reply("help me think through this architecture")

    presence = presence_store.get("tom")
    assert presence is not None
    assert presence.personality_name == "Tom"
    assert presence.current_activity is not None


def test_assistant_manager_can_set_mode(tmp_path) -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    memory_store = JSONMemoryStore(tmp_path / "memory.json")
    environment_store = JSONEnvironmentStore(tmp_path / "environment.json")
    presence_store = JSONPersonalityPresenceStore(tmp_path / "presence.json")
    llm_client = StubLLMClient()

    manager = AssistantManager(
        personality_registry=registry,
        memory_store=memory_store,
        environment_store=environment_store,
        presence_store=presence_store,
        llm_client=llm_client,
        default_personality="tom",
    )

    manager.set_mode("riding")

    assert manager.get_mode() == "riding"


def test_prompt_builder_mode_instructions_keep_brief_style_across_contexts() -> None:
    builder = PromptBuilder()

    riding = builder._format_mode("riding")
    stopped = builder._format_mode("stopped")
    parked = builder._format_mode("parked")

    assert "low distraction" in riding
    assert "same concise style" in stopped
    assert "same concise style" in parked


def test_prompt_builder_sets_global_three_sentence_cap() -> None:
    registry = PersonalityRegistry.from_directory(PERSONALITY_DIR)
    personality = registry.get("tom")
    builder = PromptBuilder()

    prompt = builder.build(
        personality=personality,
        recalled_memories=[],
        environment_events=[],
        environment_mode="parked",
        active_presence=None,
        other_presences=[],
        conversation=[],
        user_message="help me think this through",
    )

    assert "default to 1 short sentence" in prompt
    assert "Never exceed 3 sentences" in prompt
