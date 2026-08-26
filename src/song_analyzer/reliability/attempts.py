from dataclasses import dataclass, field
from datetime import datetime, timezone

from song_analyzer.reliability.failures import Failure


@dataclass(frozen=True)
class FailedAttempt:
    """Record of one unsuccessful processing attempt."""

    attempt_number: int
    failure: Failure
    raw_output: str | None = None
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )