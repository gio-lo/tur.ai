"""OpenAI-backed LLM implementation."""

from __future__ import annotations

from typing import Sequence

from tur.llm.base import ChatMessage, LLMClient
from tur.llm.development_client import DevelopmentLLMClient

try:
    from openai import APIError, APIStatusError, OpenAI, RateLimitError
except ModuleNotFoundError:  # pragma: no cover - depends on environment setup
    class APIError(Exception):
        """Fallback API error type when OpenAI SDK is unavailable."""

    class APIStatusError(APIError):
        """Fallback API status error type when OpenAI SDK is unavailable."""

    class RateLimitError(APIError):
        """Fallback rate-limit error type when OpenAI SDK is unavailable."""

    OpenAI = None


class OpenAIChatClient(LLMClient):
    """LLM client backed by the OpenAI Responses API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key) if OpenAI is not None else None
        self._model = model
        self._fallback_client = DevelopmentLLMClient()

    def generate_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        """Generate a reply using the configured OpenAI model."""
        if self._client is None:
            fallback_reply = self._fallback_client.generate_reply(system_prompt, messages)
            return (
                "The OpenAI SDK is not installed in this environment, so development fallback mode is active. "
                f"{fallback_reply}"
            )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *(
                        {"role": message.role, "content": message.content}
                        for message in messages
                    ),
                ],
            )
            content = response.choices[0].message.content or ""
            return content.strip() or "I don't have a response yet."
        except RateLimitError:
            fallback_reply = self._fallback_client.generate_reply(system_prompt, messages)
            return (
                "OpenAI API quota is unavailable right now, so development fallback mode is active. "
                f"{fallback_reply}"
            )
        except (APIStatusError, APIError) as exc:
            return (
                "OpenAI request failed, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )
        except Exception as exc:
            return (
                "OpenAI request failed unexpectedly, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )
