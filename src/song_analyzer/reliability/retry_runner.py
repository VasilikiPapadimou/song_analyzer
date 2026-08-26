import logging
from collections.abc import Callable

from song_analyzer.llm.result import LLMResult
from song_analyzer.reliability.retry import RetryPolicy

'''
        This module actually performs the retries. 
        - calls the operation, 
        - inspects the result, 
        - asks the policy what to do, and 
        - calls it again if allowed.
'''

logger = logging.getLogger(__name__)

def run_llm_with_retry(
    operation: Callable[[], LLMResult],
    policy: RetryPolicy,
) -> LLMResult:

    """Run an LLM operation with bounded retry attempts."""

    for attempt_number in range(1, policy.max_attempts + 1):
        result = operation()

        # Stop immediately when the request succeeds.
        if result.is_success:
            return result

        failure = result.failure

        # LLMResult guarantees a failed result contains a Failure.
        if failure is None:
            raise RuntimeError("Failed LLMResult did not contain a Failure.")

        # Stop when the failure or attempt number does not allow a retry.
        if not policy.should_retry(failure, attempt_number):
            return result

        logger.warning(
            "Retrying LLM request after %s. Attempt %s of %s failed.",
            failure.code,
            attempt_number,
            policy.max_attempts,
        )

    raise RuntimeError("Retry loop ended without returning an LLMResult.")