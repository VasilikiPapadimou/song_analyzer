from dataclasses import dataclass

from song_analyzer.reliability.failures import Failure, FailureCode

'''
    This module defines WHETHER another attempt is allowed
'''

# Failures that can reasonably be solved by another LLM attempt.
RETRYABLE_CODES = frozenset(
    {
        FailureCode.API_TRANSIENT_ERROR,
        FailureCode.API_RATE_LIMITED,
        FailureCode.LLM_EMPTY_RESPONSE,
        FailureCode.INVALID_JSON,
        FailureCode.SCHEMA_VALIDATION_FAILED,
    }
)


@dataclass(frozen=True)
class RetryPolicy:
    """Rules that decide whether another attempt is allowed."""
    max_attempts: int = 3

    def __post_init__(self) -> None:
        # A retry policy must allow at least the first attempt.
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

    def should_retry(self, failure: Failure, attempt_number: int) -> bool:
        """Return True when the failure and attempt allow another try."""

        # Stop when the configured attempt limit has been reached.
        if attempt_number >= self.max_attempts:
            return False

        return failure.code in RETRYABLE_CODES