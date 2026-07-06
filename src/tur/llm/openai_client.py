"""OpenAI-backed LLM implementation."""

from __future__ import annotations

from typing import Iterator, Sequence

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
    """LLM client backed by the OpenAI Chat Completions API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key) if OpenAI is not None else None
        self._model = model
        self._fallback_client = DevelopmentLLMClient()

    def generate_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        """Generate a reply using the configured OpenAI model."""
        if self._client is None:
            return self._sdk_missing_reply(system_prompt, messages)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=self._build_messages(system_prompt, messages),
            )
            content = response.choices[0].message.content or ""
            return content.strip() or "I don't have a response yet."
        except RateLimitError:
            return self._rate_limit_reply(system_prompt, messages)
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

    def stream_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> Iterator[str]:
        """Stream a reply using the configured OpenAI model."""
        if self._client is None:
            yield self._sdk_missing_reply(system_prompt, messages)
            return

        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=self._build_messages(system_prompt, messages),
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
        except RateLimitError:
            yield self._rate_limit_reply(system_prompt, messages)
        except (APIStatusError, APIError) as exc:
            yield (
                "OpenAI request failed, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )
        except Exception as exc:
            yield (
                "OpenAI request failed unexpectedly, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )

    def _build_messages(
        self,
        system_prompt: str,
        messages: Sequence[ChatMessage],
    ) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            *(
                {"role": message.role, "content": message.content}
                for message in messages
            ),
        ]

    def _sdk_missing_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        fallback_reply = self._fallback_client.generate_reply(system_prompt, messages)
        return (
            "The OpenAI SDK is not installed in this environment, so development fallback mode is active. "
            f"{fallback_reply}"
        )

    def _rate_limit_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        fallback_reply = self._fallback_client.generate_reply(system_prompt, messages)
        return (
            "OpenAI API quota is unavailable right now, so development fallback mode is active. "
            f"{fallback_reply}"
        )
