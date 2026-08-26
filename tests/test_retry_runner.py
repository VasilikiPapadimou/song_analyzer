from unittest.mock import Mock

from song_analyzer.llm.result import LLMResult
from song_analyzer.reliability.failures import Failure, FailureCode
from song_analyzer.reliability.retry import RetryPolicy
from song_analyzer.reliability.retry_runner import run_llm_with_retry


# A successful operation returns immediately.
def test_success_first_attempt() -> None:
    operation = Mock(return_value=LLMResult(output='{"status": "ok"}'))

    policy = Mock(spec=RetryPolicy)
    policy.max_attempts = 3

    result = run_llm_with_retry(
        operation=operation,
        policy=policy,
    )

    assert result.is_success is True
    assert operation.call_count == 1
    policy.should_retry.assert_not_called()


# A retry decision causes the operation to run again.
def test_retry_then_success() -> None:
    failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    operation = Mock(
        side_effect=[
            LLMResult(failure=failure),
            LLMResult(output='{"status": "ok"}'),
        ]
    )

    policy = Mock(spec=RetryPolicy)
    policy.max_attempts = 3
    policy.should_retry.return_value = True

    result = run_llm_with_retry(
        operation=operation,
        policy=policy,
    )

    assert result.is_success is True
    assert operation.call_count == 2
    policy.should_retry.assert_called_once_with(failure,1)


# A stop decision prevents another attempt.
def test_policy_stops_runner() -> None:
    failure = Failure(
        code=FailureCode.MISSING_API_KEY,
        message="API key is missing.",
    )

    operation = Mock(return_value=LLMResult(failure=failure))

    policy = Mock(spec=RetryPolicy)
    policy.max_attempts = 3
    policy.should_retry.return_value = False

    result = run_llm_with_retry(
        operation=operation,
        policy=policy,
    )

    assert result.is_success is False
    assert operation.call_count == 1
    policy.should_retry.assert_called_once_with(failure,1)


# The runner keeps retrying while the policy allows it.
def test_multiple_retries() -> None:
    failure = Failure(
        code=FailureCode.API_RATE_LIMITED,
        message="Rate limit reached.",
    )

    operation = Mock(return_value=LLMResult(failure=failure))

    policy = Mock(spec=RetryPolicy)
    policy.max_attempts = 3
    policy.should_retry.side_effect = [
        True,
        True,
        False,
    ]

    result = run_llm_with_retry(
        operation=operation,
        policy=policy,
    )

    assert result.is_success is False
    assert operation.call_count == 3
    assert policy.should_retry.call_count == 3