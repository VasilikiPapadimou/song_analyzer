"""Tests for deterministic song-analysis validation."""

from song_analyzer.validation.deterministic import validate_analysis
import pytest

def make_valid_analysis() -> dict:
    """Create a valid analysis object used by multiple tests."""

    return {
        "lyrics_analysis": {
            "themes": [
                {
                    "evidence_line_numbers": [2, 5],
                }
            ],
            "emotions": [
                {
                    "evidence_line_numbers": [3, 8],
                }
            ],
            "emotional_arc": {
                "starting_state": {
                    "evidence_line_numbers": [1, 4],
                },
                "turning_points": [
                    {
                        "evidence_line_numbers": [10],
                    }
                ],
                "ending_state": {
                    "evidence_line_numbers": [18, 20],
                },
            },
            "agency_level": {
                "evidence_line_numbers": [7, 12],
            },
            "resolution_state": {
                "evidence_line_numbers": [19, 20],
            },
        }
    }


def test_valid_analysis_has_no_findings() -> None:
    """A valid analysis should contain no errors or warnings."""

    analysis = make_valid_analysis()
    result = validate_analysis( analysis=analysis, total_lyric_lines=20)

    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []


def test_out_of_range_evidence_is_an_error() -> None:
    """An evidence line outside the lyric range should be a hard error."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["themes"][0]["evidence_line_numbers"] = [2, 25]

    result = validate_analysis( analysis=analysis, total_lyric_lines=20)

    # if one of the below is true the test fails
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "EVIDENCE_LINE_OUT_OF_RANGE"
    assert (result.errors[0].field== "lyrics_analysis.themes[0].evidence_line_numbers")
    assert "25" in result.errors[0].message
    assert result.warnings == []


def test_duplicate_evidence_is_a_warning() -> None:
    """A repeated evidence line should produce a WARNING, NOT an error."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["themes"][0]["evidence_line_numbers"] = [2, 2, 5]

    result = validate_analysis(analysis=analysis,total_lyric_lines=20)

    assert result.is_valid is True
    assert result.errors == []
    assert len(result.warnings) == 1
    assert result.warnings[0].code == "DUPLICATE_EVIDENCE_LINE"
    assert (result.warnings[0].field == "lyrics_analysis.themes[0].evidence_line_numbers")
    assert "2" in result.warnings[0].message


def test_non_integer_evidence_is_an_error() -> None:
    """Evidence references must contain integers, not numeric strings."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["themes"][0]["evidence_line_numbers"] = [2, "5"]

    result = validate_analysis(analysis=analysis, total_lyric_lines=20)

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "EVIDENCE_LINE_NOT_INTEGER"
    assert (result.errors[0].field == "lyrics_analysis.themes[0].evidence_line_numbers")
    assert "'5'" in result.errors[0].message
    assert result.warnings == []


def test_empty_evidence_list_is_an_error() -> None:
    """Every analysis claim must contain at least one evidence line."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["themes"][0]["evidence_line_numbers"] = []

    result = validate_analysis(analysis=analysis,total_lyric_lines=20)

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "EVIDENCE_LIST_EMPTY"
    assert (result.errors[0].field == "lyrics_analysis.themes[0].evidence_line_numbers")
    assert result.warnings == []


def test_evidence_field_that_is_not_a_list_is_an_error() -> None:
    """The evidence field must be a list of line numbers."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["themes"][0]["evidence_line_numbers"] = 5

    result = validate_analysis(analysis=analysis, total_lyric_lines=20)

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "EVIDENCE_NOT_LIST"
    assert (result.errors[0].field == "lyrics_analysis.themes[0].evidence_line_numbers")
    assert result.warnings == []

def test_boolean_evidence_is_an_error() -> None:
    """Boolean values must not be accepted as lyric line numbers."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["themes"][0]["evidence_line_numbers"] = [2, True]

    result = validate_analysis(analysis=analysis,total_lyric_lines=20)

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "EVIDENCE_LINE_NOT_INTEGER"
    assert (result.errors[0].field == "lyrics_analysis.themes[0].evidence_line_numbers")
    assert "True" in result.errors[0].message
    assert result.warnings == []


def test_zero_total_lyric_lines_raises_value_error() -> None:
    """The validator should reject an analysis with no lyric lines."""
    analysis = make_valid_analysis()

    with pytest.raises(ValueError, match="total_lyric_lines must be at least 1",):
        validate_analysis(analysis=analysis, total_lyric_lines=0)


def test_starting_state_without_early_evidence_is_a_warning() -> None:
    """Starting-state evidence should include an early lyric line."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["emotional_arc"]["starting_state"]["evidence_line_numbers"] = [8, 9]

    result = validate_analysis(analysis=analysis,total_lyric_lines=20)

    assert result.is_valid is True
    assert result.errors == []
    assert len(result.warnings) == 1
    assert (result.warnings[0].code == "STARTING_STATE_NO_EARLY_EVIDENCE")
    assert (result.warnings[0].field== ("lyrics_analysis.emotional_arc.starting_state.evidence_line_numbers"))


def test_ending_state_without_late_evidence_is_a_warning() -> None:
    """Ending-state evidence should include a late lyric line."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["emotional_arc"]["ending_state"]["evidence_line_numbers"] = [11, 12]

    result = validate_analysis(analysis=analysis,total_lyric_lines=20)

    assert result.is_valid is True
    assert result.errors == []
    assert len(result.warnings) == 1
    assert (result.warnings[0].code== "ENDING_STATE_NO_LATE_EVIDENCE")
    assert (result.warnings[0].field == ( "lyrics_analysis.emotional_arc.ending_state.evidence_line_numbers"))


def test_turning_points_not_chronological_is_a_warning() -> None:
    """Turning points should follow the order of their evidence lines."""

    analysis = make_valid_analysis()
    analysis["lyrics_analysis"]["emotional_arc"]["turning_points"] = [
        {"evidence_line_numbers": [14]},
        {"evidence_line_numbers": [10]}
    ]

    result = validate_analysis(analysis=analysis,total_lyric_lines=20)

    assert result.is_valid is True
    assert result.errors == []
    assert len(result.warnings) == 1
    assert (result.warnings[0].code == "TURNING_POINTS_NOT_CHRONOLOGICAL")
    assert (result.warnings[0].field == "lyrics_analysis.emotional_arc.turning_points")