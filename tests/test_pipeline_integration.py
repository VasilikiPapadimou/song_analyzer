import json
from pathlib import Path

import song_analyzer.file_handling as file_handling
import song_analyzer.pipeline as pipeline


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

    # Replace the real API call with our controlled response.
    def fake_analyze_lyrics(**kwargs) -> str:
        return json.dumps(llm_response)

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