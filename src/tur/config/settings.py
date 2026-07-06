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

    @classmethod
    def load(cls) -> "AppSettings":
        """Load settings from `.env` and process environment variables."""
        load_dotenv()

        memory_value = os.getenv("MEMORY_FILE", "data/memory.json")

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            default_personality=os.getenv("DEFAULT_PERSONALITY", "nina"),
            personality_dir=Path(os.getenv("PERSONALITY_DIR", str(DEFAULT_PERSONALITY_DIR))),
            memory_file=PROJECT_ROOT / memory_value,
        )
