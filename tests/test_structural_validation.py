import json

import pytest

from song_analyzer.validation.structural import (
    parse_json,
    validate_final_analysis,
)


# Known-valid LLM response used as the baseline for structural tests.
@pytest.fixture
def valid_llm_response() -> dict:
    return {
        "lyrics_analysis": {
            "themes": [
                {
                    "family": "change_transition",
                    "label": "Choosing a new direction",
                    "role": "primary",
                    "evidence_line_numbers": [4],
                }
            ],
            "emotions": [
                {
                    "family": "hope_empowerment",
                    "label": "Determination",
                    "role": "primary",
                    "intensity": 4,
                    "evidence_line_numbers": [3, 4],
                }
            ],
            "emotional_arc": {
                "starting_state": {
                    "emotion_family": "confusion_ambivalence",
                    "label": "Uncertainty",
                    "evidence_line_numbers": [1],
                },
                "turning_points": [
                    {
                        "from_family": "confusion_ambivalence",
                        "to_family": "hope_empowerment",
                        "evidence_line_numbers": [3],
                    }
                ],
                "ending_state": {
                    "emotion_family": "hope_empowerment",
                    "label": "Determination",
                    "evidence_line_numbers": [4],
                },
                "overall_movement": "positive_shift",
            },
            "agency_level": {
                "level": "high",
                "evidence_line_numbers": [4],
            },
            "resolution_state": {
                "status": "resolved",
                "evidence_line_numbers": [4],
            },
        },
        "uncertainty": {
            "confidence_level": "high",
            "flagged_fields": [],
        },
    }


# Adds deterministic metadata to create a complete analysis.json object.
@pytest.fixture
def valid_final_analysis(valid_llm_response: dict) -> dict:
    return {
        "metadata": {
            "schema_version": "2.0",
            "song_title": "Turning Point",
            "artist": "Example Artist",
            "processed_at": "2026-08-19T19:00:00+03:00",
            "model": "gpt-4o-mini",
            "prompt_version": "2.0",
        },
        "lyrics_analysis": valid_llm_response["lyrics_analysis"],
        "uncertainty": valid_llm_response["uncertainty"],
    }


# Valid JSON that also follows SONG_ANALYSIS_SCHEMA.
def test_parse_valid_json(valid_llm_response: dict) -> None:
    raw_response = json.dumps(valid_llm_response)

    result = parse_json(raw_response)

    assert result == valid_llm_response


# Invalid JSON syntax should fail before schema validation.
def test_parse_malformed_json() -> None:
    malformed_response = '{"lyrics_analysis":'

    result = parse_json(malformed_response)

    assert result is None


# Valid JSON syntax, but with a value rejected by the schema.
def test_parse_invalid_schema(valid_llm_response: dict) -> None:
    valid_llm_response["lyrics_analysis"]["agency_level"]["level"] = "very_high"

    raw_response = json.dumps(valid_llm_response)

    result = parse_json(raw_response)

    assert result is None


# Complete analysis should pass FINAL_ANALYSIS_SCHEMA.
def test_validate_final_analysis(valid_final_analysis: dict) -> None:
    result = validate_final_analysis(valid_final_analysis)

    assert result is True


# Invalid metadata should make the final analysis fail validation.
def test_reject_invalid_final_analysis(valid_final_analysis: dict) -> None:
    valid_final_analysis["metadata"]["schema_version"] = "999"

    result = validate_final_analysis(valid_final_analysis)

    assert result is False