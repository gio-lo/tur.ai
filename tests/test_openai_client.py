from tur.llm.base import ChatMessage
from tur.llm.openai_client import OpenAIChatClient


class _StubClient:
    def __init__(self, chat) -> None:
        self.chat = chat


class _StubChat:
    def __init__(self, completions) -> None:
        self.completions = completions


class _ChunkDelta:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _ChunkChoice:
    def __init__(self, content: str | None) -> None:
        self.delta = _ChunkDelta(content)


class _Chunk:
    def __init__(self, content: str | None) -> None:
        self.choices = [_ChunkChoice(content)]


def test_openai_client_falls_back_on_generic_failure(monkeypatch) -> None:
    client = OpenAIChatClient(api_key="test-key", model="gpt-4.1-mini")

    class FailingCompletions:
        def create(self, **kwargs):
            raise RuntimeError("boom")

    client._client = _StubClient(_StubChat(FailingCompletions()))

    reply = client.generate_reply(
        system_prompt="test",
        messages=[ChatMessage(role="user", content="hello")],
    )

    assert (
        reply
        == "OpenAI request failed unexpectedly, so I could not reach the live model. Details: RuntimeError: boom."
    )


def test_openai_client_streams_content_chunks() -> None:
    client = OpenAIChatClient(api_key="test-key", model="gpt-4.1-mini")

    class StreamingCompletions:
        def create(self, **kwargs):
            assert kwargs["stream"] is True
            return [_Chunk("hel"), _Chunk("lo"), _Chunk(None)]

    client._client = _StubClient(_StubChat(StreamingCompletions()))

    chunks = list(
        client.stream_reply(
            system_prompt="test",
            messages=[ChatMessage(role="user", content="hello")],
        )
    )

    assert chunks == ["hel", "lo"]
