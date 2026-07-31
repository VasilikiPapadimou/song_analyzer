from datetime import datetime
import json
import logging
from dotenv import load_dotenv
from API_LyricsAnalyzer import analyze_lyrics
from config import configure_logging
from file_manager import (BASE_DIR, create_song_folder, input_read,save_analysis,save_text)
from input_preprocess import (create_indexed_lines, format_indexed_lines, parse_song_input, preprocess_text)
from parser import parse_json, validate_final_analysis
from prompts import PROMPT_VERSION
from schema import SCHEMA_VERSION
from _utils import LLM_Model
from analysis_validator import validate_analysis


def main() -> None:
    """
    Process one manually imported song from its original text file
    to a validated analysis.json file.
    """

    # ------------------ APPLICATION SETUP ------------------

    configure_logging()
    load_dotenv()

    logger = logging.getLogger(__name__)
    logger.info("Song Analyzer started.")

    # Use one timestamp for both folder creation and metadata.
    processing_time = datetime.now().astimezone()

    # ------------------ INPUT STAGE ------------------

    imported_file = (BASE_DIR/"data"/"imports"/"In the End - Linkin Park.txt" )

    logger.info("Starting processing for input file: %s", imported_file)

    original_text = input_read(imported_file)

    if not original_text:
        logger.error("Processing stopped because the input file could not be read.")
        print("Could not read lyrics file.")
        return

    try:
        song_input = parse_song_input(original_text)

    except ValueError as exc:
        logger.exception("The imported file does not follow the expected structure.")
        print(f"Invalid input: {exc}")
        return

    logger.info("Parsed song input: title='%s', artist='%s'.", song_input.song_title, song_input.artist)

    # ------------------ SONG FOLDER CREATION ------------------

    song_folder = create_song_folder(artist=song_input.artist, song_title=song_input.song_title, processed_at=processing_time)

    logger.info("Created or found song folder: %s", song_folder)

    original_path = song_folder / "original_lyrics.txt"
    cleaned_path = song_folder / "cleaned_lyrics.txt"
    analysis_path = song_folder / "analysis.json"

    save_text(original_path, original_text)

    logger.info("Saved original lyrics to: %s", original_path)

    # ------------------ INPUT PREPROCESSING ------------------

    cleaned_lyrics = preprocess_text(song_input.lyrics)

    indexed_lines = create_indexed_lines(cleaned_lyrics)
    numbered_lyrics = format_indexed_lines(indexed_lines)

    save_text(cleaned_path, numbered_lyrics)

    logger.info( "Saved cleaned and numbered lyrics to: %s", cleaned_path)

    # ------------------ PROCESSING: FIRST LLM CALL ------------------

    logger.info("Submitting '%s' by '%s' for LLM analysis.", song_input.song_title, song_input.artist)

    raw_output = analyze_lyrics(artist=song_input.artist, song_title=song_input.song_title, clean_text=numbered_lyrics,)

    if not raw_output:
        logger.error( "The LLM returned no usable response for '%s' by '%s'.", song_input.song_title, song_input.artist)
        print("The LLM analysis failed.")
        return

    logger.info("Received LLM response for '%s' by '%s'.", song_input.song_title, song_input.artist)

    # ------------------ LLM OUTPUT PARSING ------------------

    llm_analysis = parse_json(raw_output)

    if llm_analysis is None:
        logger.error("The LLM response failed JSON parsing or schema validation.")
        print("JSON parsing or schema validation failed.")
        return

    # ------------------ METADATA ASSEMBLY ------------------

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "song_title": song_input.song_title,
        "artist": song_input.artist,
        "processed_at": processing_time.isoformat(
            timespec="seconds"
        ),
        "model": LLM_Model,
        "prompt_version": PROMPT_VERSION,
    }

    # ------------------ FINAL ANALYSIS OBJECT ------------------

    final_analysis = {
        "metadata": metadata,
        "lyrics_analysis": llm_analysis["lyrics_analysis"],
        "uncertainty": llm_analysis["uncertainty"],
    }

    if not validate_final_analysis(final_analysis):
        logger.error("The completed analysis object failed final validation.")
        print("Final analysis validation failed.")
        return

    # ------------------ DETERMINISTIC VALIDATION ------------------

    validation_result = validate_analysis(analysis=final_analysis, total_lyric_lines=len(indexed_lines))

    if not validation_result.is_valid:
        for issue in validation_result.errors:
            logger.error("Deterministic validation failed | code=%s | field=%s | message=%s",
                issue.code,
                issue.field,
                issue.message,
            )

        print("The analysis failed deterministic validation and was not saved.")
        return

    for issue in validation_result.warnings:
        logger.warning("Deterministic validation warning | code=%s | field=%s | message=%s",
            issue.code,
            issue.field,
            issue.message,
        )
    
    if validation_result.warnings:
        print(f"Analysis completed with {len(validation_result.warnings)} validation warning(s).")
    else:
          logger.info("Analysis passed deterministic validation with no errors or warnings.")

    # ------------------ OUTPUT STAGE ------------------

    save_analysis(analysis_path, final_analysis)

    logger.info("Saved validated analysis to: %s", analysis_path)

    logger.info("Song Analyzer completed successfully for '%s' by '%s'.", song_input.song_title, song_input.artist)

    print("\nAnalysis completed successfully.")
    print(f"Song: {song_input.song_title}")
    print(f"Artist: {song_input.artist}")
    print(f"Saved analysis: {analysis_path}")

    print("\n=== RESULT ===")
    print(json.dumps( final_analysis, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()