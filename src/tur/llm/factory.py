"""Factory helpers for LLM providers."""

from __future__ import annotations

from tur.config.settings import AppSettings
from tur.llm.base import LLMClient
from tur.llm.development_client import DevelopmentLLMClient
from tur.llm.openai_client import OpenAIChatClient


def build_llm_client(settings: AppSettings) -> LLMClient:
    """Create the appropriate LLM client for the current environment."""
    if settings.openai_api_key:
        return OpenAIChatClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    return DevelopmentLLMClient()
