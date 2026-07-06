"""Terminal chat application loop."""

from __future__ import annotations

from tur.assistant.commands import parse_command
from tur.assistant.manager import AssistantManager


HELP_TEXT = """Available commands:
/switch <name>  Switch assistant personality
/memory         Show stored memories
/remember <text> Store a memory
/help           Show this help text
/quit           Exit the assistant
"""


def run_terminal_chat(manager: AssistantManager) -> None:
    """Run the interactive terminal chat loop."""
    personality = manager.active_personality
    print(f"{personality.name}: {personality.wake_phrase}")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(f"{manager.active_personality.name}: {manager.active_personality.sleep_phrase}")
            break

        if not user_input:
            continue

        command = parse_command(user_input)
        if command:
            should_exit = _handle_command(manager, command.name, command.argument)
            if should_exit:
                break
            continue

        reply = manager.generate_reply(user_input)
        print(f"{manager.active_personality.name}: {reply}")


def _handle_command(manager: AssistantManager, name: str, argument: str) -> bool:
    if name in {"quit", "exit"}:
        print(f"{manager.active_personality.name}: {manager.active_personality.sleep_phrase}")
        return True

    if name == "switch":
        if not argument:
            available = ", ".join(manager.available_personalities())
            print(f"System: Usage: /switch <name>. Available: {available}")
            return False

        try:
            personality = manager.switch_personality(argument)
        except KeyError as exc:
            print(f"System: {exc}")
            return False

        print(f"{personality.name}: {personality.wake_phrase}")
        return False

    if name == "memory":
        memories = manager.list_memories()
        if not memories:
            print("System: No memories stored yet.")
            return False

        print("System: Stored memories:")
        for memory in memories:
            print(f"- {memory.content}")
        return False

    if name == "remember":
        if not argument:
            print("System: Usage: /remember <text>")
            return False

        manager.remember(argument)
        print("System: Memory saved.")
        return False

    if name == "help":
        print(HELP_TEXT.rstrip())
        return False

    print(f"System: Unknown command '/{name}'. Type /help for available commands.")
    return False
