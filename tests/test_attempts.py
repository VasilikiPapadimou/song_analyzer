from dataclasses import FrozenInstanceError

import pytest

from song_analyzer.reliability.attempts import FailedAttempt
from song_analyzer.reliability.failures import Failure, FailureCode


# A failed attempt stores its attempt number and failure.
def test_failed_attempt_stores_failure() -> None:
    failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    attempt = FailedAttempt(
        attempt_number=1,
        failure=failure,
    )

    assert attempt.attempt_number == 1
    assert attempt.failure == failure


# Raw output is optional because some failures produce no LLM response.
def test_raw_output_is_optional() -> None:
    failure = Failure(
        code=FailureCode.API_RATE_LIMITED,
        message="Rate limit reached.",
    )

    attempt = FailedAttempt(
        attempt_number=1,
        failure=failure,
    )

    assert attempt.raw_output is None


# Unusable LLM output can be preserved for later inspection.
def test_raw_output_is_preserved() -> None:
    failure = Failure(
        code=FailureCode.INVALID_JSON,
        message="LLM output was not valid JSON.",
    )

    attempt = FailedAttempt(
        attempt_number=2,
        failure=failure,
        raw_output="{invalid json",
    )

    assert attempt.raw_output == "{invalid json"


# Failed attempts receive a timezone-aware timestamp.
def test_timestamp_is_timezone_aware() -> None:
    failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    attempt = FailedAttempt(
        attempt_number=1,
        failure=failure,
    )

    assert attempt.occurred_at.tzinfo is not None


# Historical failure records should not change after creation.
def test_failed_attempt_is_immutable() -> None:
    failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    attempt = FailedAttempt(
        attempt_number=1,
        failure=failure,
    )

    with pytest.raises(FrozenInstanceError):
        attempt.attempt_number = 2