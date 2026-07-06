"""OpenAI-backed LLM implementation."""

from __future__ import annotations

from typing import Sequence

from openai import OpenAI

from tur.llm.base import ChatMessage, LLMClient


class OpenAIChatClient(LLMClient):
    """LLM client backed by the OpenAI Responses API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate_reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        """Generate a reply using the configured OpenAI model."""
        response = self._client.responses.create(
            model=self._model,
            instructions=system_prompt,
            input=[
                *(
                    {
                        "role": message.role,
                        "content": [{"type": "input_text", "text": message.content}],
                    }
                    for message in messages
                ),
            ],
        )
        return response.output_text.strip() or "I don't have a response yet."
