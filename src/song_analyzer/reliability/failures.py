from dataclasses import dataclass
from enum import StrEnum


class FailureCode(StrEnum):
    """Standard failure codes used across the pipeline."""

    # Input / configuration
    INPUT_FILE_NOT_FOUND = "INPUT_FILE_NOT_FOUND"
    INPUT_FILE_READ_ERROR = "INPUT_FILE_READ_ERROR"
    INPUT_ENCODING_ERROR = "INPUT_ENCODING_ERROR"
    INPUT_FORMAT_INVALID = "INPUT_FORMAT_INVALID"
    DUPLICATE_ANALYSIS = "DUPLICATE_ANALYSIS"
    MISSING_API_KEY = "MISSING_API_KEY"

    # API / LLM
    API_TRANSIENT_ERROR = "API_TRANSIENT_ERROR"
    API_RATE_LIMITED = "API_RATE_LIMITED"
    API_REQUEST_ERROR = "API_REQUEST_ERROR"
    LLM_EMPTY_RESPONSE = "LLM_EMPTY_RESPONSE"

    # Validation
    INVALID_JSON = "INVALID_JSON"
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    FINAL_SCHEMA_FAILED = "FINAL_SCHEMA_FAILED"
    DETERMINISTIC_VALIDATION_FAILED = "DETERMINISTIC_VALIDATION_FAILED"

    # Storage
    OUTPUT_WRITE_ERROR = "OUTPUT_WRITE_ERROR"
    FAILED_ATTEMPT_WRITE_ERROR = "FAILED_ATTEMPT_WRITE_ERROR"


@dataclass(frozen=True)
class Failure:
    """Structured description of one pipeline failure."""

    code: FailureCode
    message: str
    details: tuple[str, ...] = ()