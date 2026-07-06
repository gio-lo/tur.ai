"""Terminal command parsing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ParsedCommand:
    """Represents a parsed terminal command."""

    name: str
    argument: str = ""


def parse_command(raw_text: str) -> ParsedCommand | None:
    """Parse slash commands from terminal input."""
    text = raw_text.strip()
    if not text.startswith("/"):
        return None

    parts = text[1:].split(maxsplit=1)
    name = parts[0].lower() if parts else ""
    argument = parts[1].strip() if len(parts) > 1 else ""
    return ParsedCommand(name=name, argument=argument)
