from unittest.mock import Mock
import httpx
from openai import RateLimitError,APIConnectionError,APIStatusError 

from song_analyzer.llm.client import analyze_lyrics
from song_analyzer.reliability.failures import FailureCode


# ERROR: Missing API configuration returns a structured failure.
def test_missing_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.output is None
    assert result.failure is not None
    assert result.failure.code == FailureCode.MISSING_API_KEY


# A successful API response is returned inside LLMResult.
def test_success_response(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    # Create a fake OpenAI response.
    mock_response = Mock()
    mock_response.output_text = '{"status": "ok"}'

    # Create a fake client that returns our response.
    mock_client = Mock()
    mock_client.responses.create.return_value = mock_response

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is True
    assert result.output == '{"status": "ok"}'
    assert result.failure is None


# An empty API response becomes a structured failure.
def test_empty_response(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    # Create a fake response with no usable output.
    mock_response = Mock()
    mock_response.output_text = ""

    # Make the fake client return the empty response.
    mock_client = Mock()
    mock_client.responses.create.return_value = mock_response

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.output is None
    assert result.failure is not None
    assert result.failure.code == FailureCode.LLM_EMPTY_RESPONSE


# A rate-limit error receives its own failure code.
def test_rate_limit(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    # Build a fake 429 response like the OpenAI SDK would receive.
    request = httpx.Request("POST","https://api.openai.com/v1/responses")
    response = httpx.Response(429, request=request)

    rate_limit_error = RateLimitError(
        "Rate limit exceeded.",
        response=response,
        body=None,
    )

    # Make the fake client raise the error instead of returning a response.
    mock_client = Mock()
    mock_client.responses.create.side_effect = rate_limit_error

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.failure is not None
    assert result.failure.code == FailureCode.API_RATE_LIMITED


# A connection error is classified as a temporary API failure.
def test_connection_error(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    request = httpx.Request("POST","https://api.openai.com/v1/responses")

    connection_error = APIConnectionError(
        request=request,
    )

    # Make the fake client raise a connection error.
    mock_client = Mock()
    mock_client.responses.create.side_effect = connection_error

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.failure is not None
    assert result.failure.code == FailureCode.API_TRANSIENT_ERROR


# A temporary server error is classified as a transient API failure.
def test_server_error(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    request = httpx.Request("POST","https://api.openai.com/v1/responses")
    response = httpx.Response(500,request=request)

    server_error = APIStatusError(
        "Internal server error.",
        response=response,
        body=None,
    )

    # Make the fake client raise a server-side API error.
    mock_client = Mock()
    mock_client.responses.create.side_effect = server_error

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.failure is not None
    assert result.failure.code == FailureCode.API_TRANSIENT_ERROR


# A bad request is classified as a non-transient API failure.
def test_request_error(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    request = httpx.Request("POST","https://api.openai.com/v1/responses")
    response = httpx.Response(400,request=request)

    request_error = APIStatusError(
        "Bad request.",
        response=response,
        body=None,
    )

    # Make the fake client raise a bad-request API error.
    mock_client = Mock()
    mock_client.responses.create.side_effect = request_error

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.failure is not None
    assert result.failure.code == FailureCode.API_REQUEST_ERROR


# An unexpected client error becomes a general request failure.
def test_unexpected_error(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    # Simulate an unexpected error inside the API call.
    mock_client = Mock()
    mock_client.responses.create.side_effect = RuntimeError("Unexpected client problem.")

    monkeypatch.setattr(
        "song_analyzer.llm.client.OpenAI",
        lambda **kwargs: mock_client,
    )

    result = analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert result.is_success is False
    assert result.failure is not None
    assert result.failure.code == FailureCode.API_REQUEST_ERROR

# SDK retries stay disabled so our retry layer owns retry decisions.
def test_sdk_retries_disabled(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    mock_response = Mock()
    mock_response.output_text = '{"status": "ok"}'

    mock_client = Mock()
    mock_client.responses.create.return_value = mock_response

    captured_kwargs = {}

    def fake_openai(**kwargs):
        captured_kwargs.update(kwargs)
        return mock_client

    monkeypatch.setattr("song_analyzer.llm.client.OpenAI", fake_openai)

    analyze_lyrics(
        artist="Example Artist",
        song_title="Example Song",
        clean_text="[1] Example lyric",
    )

    assert captured_kwargs["max_retries"] == 0