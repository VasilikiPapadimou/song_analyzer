import json
from pathlib import Path
from unittest.mock import Mock

import song_analyzer.file_handling as file_handling
import song_analyzer.pipeline as pipeline
from song_analyzer.llm.result import LLMResult
from song_analyzer.reliability.failures import Failure, FailureCode


def test_pipeline_success(tmp_path: Path, monkeypatch) -> None:
    # Create a temporary song input.
    input_path = tmp_path / "song.txt"
    input_path.write_text(
        "Example Artist\n"
        "Turning Point\n"
        "I walked beneath the quiet sky\n"
        "Carrying questions through the night\n"
        "The morning opened up ahead\n"
        "And I chose a different road",
        encoding="utf-8",
    )

    # Keep generated files outside the real data/exports folder.
    output_dir = tmp_path / "exports"
    monkeypatch.setattr(file_handling, "DATA_DIR", output_dir)

    # Known-valid response returned instead of calling OpenAI.
    llm_response = {
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

    # Return the same result type as the real LLM client.
    def fake_analyze_lyrics(**kwargs) -> LLMResult:
        return LLMResult(
            output=json.dumps(llm_response)
        )

    monkeypatch.setattr(pipeline,"analyze_lyrics",fake_analyze_lyrics)

    # Run the real pipeline.
    pipeline.run_pipeline(input_path)

    analysis_files = list(output_dir.rglob("analysis.json"))

    assert len(analysis_files) == 1

    saved_analysis = json.loads(
        analysis_files[0].read_text(encoding="utf-8")
    )

    assert saved_analysis["metadata"]["artist"] == "Example Artist"
    assert saved_analysis["metadata"]["song_title"] == "Turning Point"
    assert saved_analysis["lyrics_analysis"] == llm_response["lyrics_analysis"]
    assert saved_analysis["uncertainty"] == llm_response["uncertainty"]


# A failed LLM request stops the pipeline without saving analysis.json.
def test_pipeline_llm_failure(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "song.txt"
    input_path.write_text(
        "Example Artist\n"
        "Turning Point\n"
        "I walked beneath the quiet sky\n"
        "And I chose a different road",
        encoding="utf-8",
    )

    # Keep generated files outside the real exports folder.
    output_dir = tmp_path / "exports"
    monkeypatch.setattr(file_handling, "DATA_DIR", output_dir)

    # Simulate a structured failure from the LLM client.
    def fake_analyze_lyrics(**kwargs) -> LLMResult:
        return LLMResult(
            failure=Failure(
                code=FailureCode.API_REQUEST_ERROR,
                message="The LLM API request failed.",
            )
        )

    monkeypatch.setattr(
        pipeline,
        "analyze_lyrics",
        fake_analyze_lyrics,
    )

    pipeline.run_pipeline(input_path)

    analysis_files = list(output_dir.rglob("analysis.json"))

    assert analysis_files == []

"""-----------------------------------------RETRY CHECK-----------------------------------------"""

# A transient LLM failure is retried and can recover successfully.
def test_pipeline_retries_then_succeeds(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "song.txt"
    input_path.write_text(
        "Example Artist\n"
        "Turning Point\n"
        "I walked beneath the quiet sky\n"
        "Carrying questions through the night\n"
        "The morning opened up ahead\n"
        "And I chose a different road",
        encoding="utf-8",
    )

    output_dir = tmp_path / "exports"
    monkeypatch.setattr(file_handling, "DATA_DIR", output_dir)

    llm_response = {
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

    transient_failure = Failure(
        code=FailureCode.API_TRANSIENT_ERROR,
        message="Temporary API failure.",
    )

    mock_analyze = Mock(
        side_effect=[
            LLMResult(failure=transient_failure),
            LLMResult(output=json.dumps(llm_response)),
        ]
    )

    monkeypatch.setattr(
        pipeline,
        "analyze_lyrics",
        mock_analyze,
    )

    pipeline.run_pipeline(input_path)

    analysis_files = list(output_dir.rglob("analysis.json"))

    assert mock_analyze.call_count == 2
    assert len(analysis_files) == 1

    failed_attempt_files = list(output_dir.rglob("failed_attempts/attempt_1.json"))
    assert len(failed_attempt_files) == 1


    failed_attempt_data = json.loads(failed_attempt_files[0].read_text(encoding="utf-8"))

    assert failed_attempt_data["attempt_number"] == 1
    assert failed_attempt_data["failure"]["code"] == "API_TRANSIENT_ERROR"
    assert failed_attempt_data["failure"]["message"] == "Temporary API failure."
    assert failed_attempt_data["raw_output"] is None