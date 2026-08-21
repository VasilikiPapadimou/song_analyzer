from dataclasses import dataclass

from song_analyzer.reliability.failures import Failure


@dataclass(frozen=True)
class LLMResult:
    """Result of one LLM request."""

    output: str | None = None
    failure: Failure | None = None

    def __post_init__(self) -> None:
        has_output = self.output is not None
        has_failure = self.failure is not None

        if has_output == has_failure:
            raise ValueError("LLMResult must contain exactly one of output or failure.")

    @property
    def is_success(self) -> bool:
        return self.output is not None