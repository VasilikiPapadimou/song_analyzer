import pytest

from song_analyzer.reliability.failures import Failure, FailureCode
from song_analyzer.reliability.retry import RetryPolicy

""" 
    This module decides WHETHER another attempt is allowed

"""

# A retryable failure can retry while attempts remain.
def test_retryable_failure() -> None:
    policy = RetryPolicy(max_attempts=3)

    failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    assert policy.should_retry(failure, attempt_number=1) is True


# A non-retryable failure stops immediately.
def test_non_retryable_failure() -> None:
    policy = RetryPolicy(max_attempts=3)

    failure = Failure(
        code=FailureCode.MISSING_API_KEY,
        message="API key is missing.",
    )

    assert policy.should_retry(failure, attempt_number=1) is False


# A retryable failure stops when the attempt limit is reached.
def test_attempt_limit() -> None:
    policy = RetryPolicy(max_attempts=3)

    failure = Failure(
        code=FailureCode.API_RATE_LIMITED,
        message="Rate limit reached.",
    )

    assert policy.should_retry(failure, attempt_number=3) is False


# A policy must allow at least one attempt.
def test_invalid_max_attempts() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)