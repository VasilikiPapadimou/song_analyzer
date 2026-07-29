""" ------------------ Deterministic validation for structured song analyses. ------------------
This module checks facts that Python can verify without interpreting the meaning of the lyrics.
"""
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    """Clarifies the fields of one specific validation error or warning."""
    code: str
    field: str
    message: str


@dataclass
class ValidationResult:
    """
    All deterministic validation findings for one analysis.
        Errors and warnings are stored separately.
        is_valid is derived only from whether hard errors exist.
    """

    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def iter_evidence_fields(value: Any, path: str = "" ) -> Iterator[tuple[str, Any]]:
    """
    Find every evidence_line_numbers field inside the analysis.json.
    Yields: 
        The complete JSON path and the field's current value.
    """

    if isinstance(value, dict):
        for key, nested_value in value.items():
            current_path = f"{path}.{key}" if path else key

            if key == "evidence_line_numbers":
                yield current_path, nested_value
            else:
                yield from iter_evidence_fields(
                    nested_value,
                    current_path,
                )

    elif isinstance(value, list):
        for index, item in enumerate(value):
            current_path = f"{path}[{index}]"

            yield from iter_evidence_fields(
                item,
                current_path,
            )

#--------------------------------ERROR / WARNING Creation-structure--------------------------------

def validate_evidence_references(analysis: dict[str, Any], total_lyric_lines: int) -> ValidationResult:
    """
        Validate every evidence line reference against the cleaned lyrics.

        Hard errors make the analysis invalid.
        Duplicate references are reported as warnings.
    """

    if total_lyric_lines < 1:
        raise ValueError("total_lyric_lines must be at least 1." )

    result = ValidationResult()

    for evidence_path, evidence_lines in iter_evidence_fields(analysis):
        # The evidence field must contain a JSON array.
        if not isinstance(evidence_lines, list):
            result.errors.append(
                ValidationIssue(
                    code="EVIDENCE_NOT_LIST",
                    field=evidence_path,
                    message=("Evidence line numbers must be provided as a list."),
                )
            )
            continue

        # A claim without supporting evidence is not accepted.
        if not evidence_lines:
            result.errors.append(
                ValidationIssue(
                    code="EVIDENCE_LIST_EMPTY",
                    field=evidence_path,
                    message=("At least one evidence line is required."),
                )
            )
            continue

        seen_line_numbers: set[int] = set()

        for line_number in evidence_lines:
            if type(line_number) is not int:
                result.errors.append(
                    ValidationIssue(
                        code="EVIDENCE_LINE_NOT_INTEGER",
                        field=evidence_path,
                        message=(f"Evidence line values must be integers. Received: {line_number!r}.")
                    )
                )
                continue

            if not 1 <= line_number <= total_lyric_lines:
                result.errors.append(
                    ValidationIssue(
                        code="EVIDENCE_LINE_OUT_OF_RANGE",
                        field=evidence_path,
                        message=(f"Evidence line {line_number} does not exist. Valid range: 1-{total_lyric_lines}."),
                    )
                )
                continue

            if line_number in seen_line_numbers:
                result.warnings.append(
                    ValidationIssue(
                        code="DUPLICATE_EVIDENCE_LINE",
                        field=evidence_path,
                        message=(f"Evidence line {line_number} appears more than once in the same field.")
                    )
                )
                continue

            seen_line_numbers.add(line_number)

    return result

#-------------------------------- Positional Warnings--------------------------------
def get_valid_line_numbers(evidence_lines: Any, total_lyric_lines: int) -> list[int]:
    """Return only valid integer evidence references."""

    if not isinstance(evidence_lines, list):
        return []

    return [
        line_number
        for line_number in evidence_lines
        if (
            type(line_number) is int
            and 1 <= line_number <= total_lyric_lines
        )
    ]


def validate_emotional_arc_positions(analysis: dict[str, Any], total_lyric_lines: int) -> ValidationResult:
    """
    Check whether emotional-arc evidence follows a plausible order.

    These checks produce warnings because song structures can repeat
    or return to earlier emotional states.
    """

    if total_lyric_lines < 1:
        raise ValueError("total_lyric_lines must be at least 1.")

    result = ValidationResult()

    emotional_arc = analysis["lyrics_analysis"]["emotional_arc"]
    first_section_end = max(1,(total_lyric_lines + 2) // 3)
    final_section_start = max(1, (2 * total_lyric_lines) // 3 + 1)

    starting_lines = get_valid_line_numbers(
        emotional_arc["starting_state"]["evidence_line_numbers"],
        total_lyric_lines
    )

    ending_lines = get_valid_line_numbers(
        emotional_arc["ending_state"]["evidence_line_numbers"],
        total_lyric_lines
    )

    # Starting-state evidence should include something near the beginning.
    if starting_lines and min(starting_lines) > first_section_end:
        result.warnings.append(
            ValidationIssue(
                code="STARTING_STATE_NO_EARLY_EVIDENCE",
                field=("lyrics_analysis.emotional_arc.starting_state.evidence_line_numbers"),
                message=(f"Starting-state evidence does not include any line from the first {first_section_end} lyric lines."),
            )
        )

    # Ending-state evidence should include something near the ending.
    if ending_lines and max(ending_lines) < final_section_start:
        result.warnings.append(
            ValidationIssue(
                code="ENDING_STATE_NO_LATE_EVIDENCE",
                field=("lyrics_analysis.emotional_arc.ending_state.evidence_line_numbers"),
                message=(f"Ending-state evidence does not include any line from line {final_section_start} to the end."),
            )
        )

    # Turning Point should be checked in the overall text
    turning_point_positions: list[int] = []

    for turning_point in emotional_arc["turning_points"]:
        valid_lines = get_valid_line_numbers(turning_point["evidence_line_numbers"],total_lyric_lines)

        if valid_lines:
            # The first referenced line marks where the transition begins.
            turning_point_positions.append(min(valid_lines))

    for previous, current in zip(turning_point_positions, turning_point_positions[1:]):
        if current <= previous:
            result.warnings.append(
                ValidationIssue(
                    code="TURNING_POINTS_NOT_CHRONOLOGICAL",
                    field=("lyrics_analysis.emotional_arc.turning_points"),
                    message=("Turning points are not ordered chronologically by their evidence lines.")
                )
            )
            break

    return result

# ----------------------------------------Results of the validators above ----------------------------------------
def validate_analysis(analysis: dict[str, Any], total_lyric_lines: int) -> ValidationResult:
    """
    Run all deterministic checks after schema validation.

    The findings from the individual validators are combined into one ValidationResult.
    """

    evidence_result = validate_evidence_references( analysis=analysis,total_lyric_lines=total_lyric_lines)

    arc_position_result = validate_emotional_arc_positions(analysis=analysis, total_lyric_lines=total_lyric_lines)

    combined_result = ValidationResult()

    combined_result.errors.extend(evidence_result.errors)
    combined_result.errors.extend(arc_position_result.errors)

    combined_result.warnings.extend(evidence_result.warnings)
    combined_result.warnings.extend(arc_position_result.warnings)

    return combined_result