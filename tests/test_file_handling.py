from datetime import datetime, timezone
from pathlib import Path
import json


from song_analyzer.file_handling import ( create_song_folder, get_current_week_id, input_read,
    make_path_safe, save_analysis, save_failed_attempt, save_text)
import song_analyzer.file_handling as file_handling
from song_analyzer.reliability.attempts import FailedAttempt
from song_analyzer.reliability.failures import Failure, FailureCode


# Existing UTF-8 file should be read successfully.
def test_read_existing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "song.txt"
    file_path.write_text("Example lyrics", encoding="utf-8")

    result = input_read(file_path)

    assert result == "Example lyrics"


# Missing file should return an empty string.
def test_read_missing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.txt"

    result = input_read(file_path)

    assert result == ""


# Fixed date should produce the correct ISO week ID.
def test_get_week_id() -> None:
    processed_at = datetime(2026, 1, 1)

    result = get_current_week_id(processed_at)

    assert result == "2026-W01"


# Folder names should be normalized for safe filesystem use.
def test_make_path_safe() -> None:
    result = make_path_safe("  Turning Point!  ")

    assert result == "turning_point"


# Song folder should be created under the correct week and date.
def test_create_song_folder(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(file_handling, "DATA_DIR", tmp_path)

    processed_at = datetime(2026, 8, 21)

    result = create_song_folder(
        artist="Example Artist",
        song_title="Turning Point",
        processed_at=processed_at,
    )

    expected = (tmp_path/ "2026-W34"/ "turning_point_example_artist_2026-08-21"
    )

    assert result == expected
    assert result.exists()
    assert result.is_dir()


# Text content should be saved exactly as provided.
def test_save_text(tmp_path: Path) -> None:
    file_path = tmp_path / "output" / "cleaned_lyrics.txt"

    result = save_text(file_path, "Example lyrics")

    assert result == file_path
    assert file_path.read_text(encoding="utf-8") == "Example lyrics"


# Analysis dictionary should be saved as valid JSON.
def test_save_analysis(tmp_path: Path) -> None:
    file_path = tmp_path / "output" / "analysis.json"

    analysis = {
        "song": "Turning Point",
        "confidence": "high",
    }

    result = save_analysis(file_path, analysis)

    saved_data = json.loads(file_path.read_text(encoding="utf-8"))

    assert result == file_path
    assert saved_data == analysis


# Failed attempt data should be saved as inspectable JSON.
def test_save_failed_attempt(tmp_path: Path) -> None:
    failure = Failure(
        code=FailureCode.INVALID_JSON,
        message="LLM output was not valid JSON.",
        details=("Unexpected token.",),
    )

    attempt = FailedAttempt(
        attempt_number=2,
        failure=failure,
        raw_output="{invalid json",
        occurred_at=datetime(
            2026,
            8,
            26,
            17,
            30,
            tzinfo=timezone.utc,
        ),
    )

    song_folder = tmp_path / "example_song"

    result = save_failed_attempt(
        song_folder=song_folder,
        attempt=attempt,
        model="gpt-4o-mini",
        prompt_version="2.0",
    )

    expected_path = (song_folder/ "failed_attempts"/ "attempt_2.json")

    saved_data = json.loads(expected_path.read_text(encoding="utf-8"))

    assert result == expected_path
    assert saved_data == {
        "attempt_number": 2,
        "occurred_at": "2026-08-26T17:30:00+00:00",
        "model": "gpt-4o-mini",
        "prompt_version": "2.0",
        "failure": {
            "code": "INVALID_JSON",
            "message": "LLM output was not valid JSON.",
            "details": ["Unexpected token."],
        },
        "raw_output": "{invalid json",
    }