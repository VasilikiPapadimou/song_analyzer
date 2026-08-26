""" This Module tests this rule 
     LLMResult must contain:
     output  OR  failure
     never both
     never neither
"""
import pytest

from song_analyzer.llm.result import LLMResult
from song_analyzer.reliability.failures import Failure, FailureCode


# A successful request contains output and no failure.
def test_success_result() -> None:
    result = LLMResult(output='{"status": "ok"}')

    assert result.output == '{"status": "ok"}'
    assert result.failure is None
    assert result.is_success is True


# A failed request contains a Failure and no output.
def test_failure_result() -> None:
    failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    result = LLMResult(failure=failure)

    assert result.output is None
    assert result.failure == failure
    assert result.is_success is False


# A result cannot represent success and failure at the same time.
def test_reject_both_values() -> None:
    failure = Failure(
        code=FailureCode.API_REQUEST_ERROR,
        message="API request failed.",
    )

    with pytest.raises(ValueError):
        LLMResult(
            output='{"status": "ok"}',
            failure=failure,
        )


# A result must contain either output or a failure.
def test_reject_empty_result() -> None:
    with pytest.raises(ValueError):
        LLMResult()