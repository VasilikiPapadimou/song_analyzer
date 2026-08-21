from dataclasses import FrozenInstanceError
import pytest
from song_analyzer.reliability.failures import Failure, FailureCode


# Failure codes behave as stable string values.
def test_failure_code() -> None:
    assert FailureCode.INVALID_JSON == "INVALID_JSON"


# Failure stores the code, message and default empty details.
def test_create_failure() -> None:
    failure = Failure(
        code=FailureCode.INVALID_JSON,
        message="LLM response was not valid JSON.",
    )

    assert failure.code == FailureCode.INVALID_JSON
    assert failure.message == "LLM response was not valid JSON."
    assert failure.details == ()


# Optional details can preserve extra failure information.
def test_failure_details() -> None:
    failure = Failure(
        code=FailureCode.DETERMINISTIC_VALIDATION_FAILED,
        message="Analysis failed deterministic validation.",
        details=(
            "Evidence line 12 does not exist.",
            "Valid range is 1-8.",
        ),
    )

    assert len(failure.details) == 2
    assert failure.details[0] == "Evidence line 12 does not exist."


# A recorded failure should not be modified after creation.
def test_failure_is_immutable() -> None:
    failure = Failure(
        code=FailureCode.INVALID_JSON,
        message="LLM response was not valid JSON.",
    )

    with pytest.raises(FrozenInstanceError):
        failure.message = "Changed message"