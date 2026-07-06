from tur.llm.base import ChatMessage
from tur.llm.openai_client import OpenAIChatClient


class _RetryableAPIError(Exception):
    pass


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
    captured_kwargs = {}

    class StreamingCompletions:
        def create(self, **kwargs):
            captured_kwargs.update(kwargs)
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
    assert captured_kwargs["max_completion_tokens"] == 120
    assert "reasoning_effort" not in captured_kwargs
    assert "verbosity" not in captured_kwargs


def test_openai_client_stops_cleanly_on_keyboard_interrupt() -> None:
    client = OpenAIChatClient(api_key="test-key", model="gpt-4.1-mini")

    class InterruptingCompletions:
        def create(self, **kwargs):
            raise KeyboardInterrupt

    client._client = _StubClient(_StubChat(InterruptingCompletions()))

    chunks = list(
        client.stream_reply(
            system_prompt="test",
            messages=[ChatMessage(role="user", content="hello")],
        )
    )

    assert chunks == []


def test_openai_client_retries_without_unsupported_verbosity() -> None:
    client = OpenAIChatClient(api_key="test-key", model="gpt-4.1-mini", verbosity="low")
    calls = []

    class Message:
        def __init__(self, content: str) -> None:
            self.content = content

    class Choice:
        def __init__(self, content: str) -> None:
            self.message = Message(content)

    class Response:
        def __init__(self, content: str) -> None:
            self.choices = [Choice(content)]

    class RetryCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise _RetryableAPIError(
                    "Error code: 400 - {'error': {'message': "
                    "\"Unsupported value: 'verbosity' does not support 'low' with this model.\", "
                    "'param': 'verbosity'}}"
                )
            return Response("ok")

    client._client = _StubClient(_StubChat(RetryCompletions()))

    reply = client.generate_reply(
        system_prompt="test",
        messages=[ChatMessage(role="user", content="hello")],
    )

    assert reply == "ok"
    assert calls[0]["verbosity"] == "low"
    assert "verbosity" not in calls[1]


def test_openai_client_retries_without_unrecognized_reasoning_effort() -> None:
    client = OpenAIChatClient(api_key="test-key", model="gpt-4.1-mini", reasoning_effort="low")
    calls = []

    class Message:
        def __init__(self, content: str) -> None:
            self.content = content

    class Choice:
        def __init__(self, content: str) -> None:
            self.message = Message(content)

    class Response:
        def __init__(self, content: str) -> None:
            self.choices = [Choice(content)]

    class RetryCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise _RetryableAPIError(
                    "Error code: 400 - {'error': {'message': "
                    "'Unrecognized request argument supplied: reasoning_effort', "
                    "'type': 'invalid_request_error'}}"
                )
            return Response("ok")

    client._client = _StubClient(_StubChat(RetryCompletions()))

    reply = client.generate_reply(
        system_prompt="test",
        messages=[ChatMessage(role="user", content="hello")],
    )

    assert reply == "ok"
    assert calls[0]["reasoning_effort"] == "low"
    assert "reasoning_effort" not in calls[1]
