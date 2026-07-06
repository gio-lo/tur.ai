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

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_completion_tokens: int = 120,
        reasoning_effort: str | None = None,
        verbosity: str | None = None,
    ) -> None:
        self._client = OpenAI(api_key=api_key) if OpenAI is not None else None
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._max_completion_tokens = max_completion_tokens
        self._reasoning_effort = reasoning_effort
        self._verbosity = verbosity
        self._fallback_client = DevelopmentLLMClient()

    def generate_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        """Generate a reply using the configured OpenAI model."""
        if self._client is None:
            return self._sdk_missing_reply(system_prompt, messages)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=self._build_messages(system_prompt, messages),
                **self._request_options(),
            )
            content = response.choices[0].message.content or ""
            return content.strip() or "I don't have a response yet."
        except RateLimitError:
            return self._rate_limit_reply(system_prompt, messages)
        except (APIStatusError, APIError) as exc:
            retry_options = self._retryable_request_options(exc)
            if retry_options is not None:
                return self._retry_generate_reply(system_prompt, messages, retry_options, exc)
            return (
                "OpenAI request failed, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )
        except Exception as exc:
            retry_options = self._retryable_request_options(exc)
            if retry_options is not None:
                return self._retry_generate_reply(system_prompt, messages, retry_options, exc)
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
                **self._request_options(),
            )
            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
        except RateLimitError:
            yield self._rate_limit_reply(system_prompt, messages)
        except KeyboardInterrupt:
            return
        except (APIStatusError, APIError) as exc:
            retry_options = self._retryable_request_options(exc)
            if retry_options is not None:
                yield from self._retry_stream_reply(system_prompt, messages, retry_options, exc)
                return
            yield (
                "OpenAI request failed, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )
        except Exception as exc:
            retry_options = self._retryable_request_options(exc)
            if retry_options is not None:
                yield from self._retry_stream_reply(system_prompt, messages, retry_options, exc)
                return
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

    def _request_options(self) -> dict[str, str | float | int]:
        options: dict[str, str | float | int] = {
            "timeout": self._timeout_seconds,
            "max_completion_tokens": self._max_completion_tokens,
        }
        if self._reasoning_effort:
            options["reasoning_effort"] = self._reasoning_effort
        if self._verbosity:
            options["verbosity"] = self._verbosity
        return options

    def _retryable_request_options(self, exc: Exception) -> dict[str, str | float | int] | None:
        error_text = str(exc)
        retry_options = self._request_options()
        changed = False

        if self._mentions_option(error_text, "verbosity"):
            retry_options.pop("verbosity", None)
            changed = True

        if self._mentions_option(error_text, "reasoning_effort"):
            retry_options.pop("reasoning_effort", None)
            changed = True

        return retry_options if changed else None

    def _mentions_option(self, error_text: str, option_name: str) -> bool:
        quoted = f"'{option_name}'"
        unsupported_value = quoted in error_text and "Unsupported value" in error_text
        unrecognized_argument = option_name in error_text and "Unrecognized request argument supplied" in error_text
        return unsupported_value or unrecognized_argument

    def _retry_generate_reply(
        self,
        system_prompt: str,
        messages: Sequence[ChatMessage],
        retry_options: dict[str, str | float | int],
        original_exc: Exception,
    ) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=self._build_messages(system_prompt, messages),
                **retry_options,
            )
            content = response.choices[0].message.content or ""
            return content.strip() or "I don't have a response yet."
        except RateLimitError:
            return self._rate_limit_reply(system_prompt, messages)
        except Exception as retry_exc:
            exc = retry_exc or original_exc
            return (
                "OpenAI request failed, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )

    def _retry_stream_reply(
        self,
        system_prompt: str,
        messages: Sequence[ChatMessage],
        retry_options: dict[str, str | float | int],
        original_exc: Exception,
    ) -> Iterator[str]:
        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=self._build_messages(system_prompt, messages),
                stream=True,
                **retry_options,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
        except RateLimitError:
            yield self._rate_limit_reply(system_prompt, messages)
        except KeyboardInterrupt:
            return
        except Exception as retry_exc:
            exc = retry_exc or original_exc
            yield (
                "OpenAI request failed, so I could not reach the live model. "
                f"Details: {exc.__class__.__name__}: {exc}."
            )

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
