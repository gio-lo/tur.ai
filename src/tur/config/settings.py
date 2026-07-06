"""Application configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
DEFAULT_PERSONALITY_DIR = SRC_ROOT / "tur" / "personalities"


@dataclass(slots=True)
class AppSettings:
    """Runtime settings loaded from the environment."""

    openai_api_key: str | None
    openai_model: str
    default_personality: str
    personality_dir: Path
    memory_file: Path
    environment_file: Path
    presence_file: Path
    max_history_messages: int
    max_personality_references: int
    fallback_personality_references: int
    max_reference_characters: int
    max_environment_events: int
    openai_timeout_seconds: float
    openai_max_completion_tokens: int
    openai_reasoning_effort: str | None
    openai_verbosity: str | None

    @classmethod
    def load(cls) -> "AppSettings":
        """Load settings from `.env` and process environment variables."""
        load_dotenv()

        memory_value = os.getenv("MEMORY_FILE", "data/memory.json")
        environment_value = os.getenv("ENVIRONMENT_FILE", "data/environment.json")
        presence_value = os.getenv("PRESENCE_FILE", "data/presence.json")

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            default_personality=os.getenv("DEFAULT_PERSONALITY", "nina"),
            personality_dir=Path(os.getenv("PERSONALITY_DIR", str(DEFAULT_PERSONALITY_DIR))),
            memory_file=PROJECT_ROOT / memory_value,
            environment_file=PROJECT_ROOT / environment_value,
            presence_file=PROJECT_ROOT / presence_value,
            max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "4")),
            max_personality_references=int(os.getenv("MAX_PERSONALITY_REFERENCES", "1")),
            fallback_personality_references=int(os.getenv("FALLBACK_PERSONALITY_REFERENCES", "0")),
            max_reference_characters=int(os.getenv("MAX_REFERENCE_CHARACTERS", "600")),
            max_environment_events=int(os.getenv("MAX_ENVIRONMENT_EVENTS", "2")),
            openai_timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30")),
            openai_max_completion_tokens=int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "120")),
            openai_reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT") or None,
            openai_verbosity=os.getenv("OPENAI_VERBOSITY") or None,
        )
