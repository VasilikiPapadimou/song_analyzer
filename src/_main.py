from dotenv import load_dotenv
import json
from file_manager import ( BASE_DIR, create_song_folder, input_read, save_analysis, save_text)
from input_preprocess import (create_indexed_lines, format_indexed_lines, parse_song_input, preprocess_text)
from API_LyricsAnalyzer import analyze_lyrics
from parser import parse_json
from config import configure_logging
import logging

def main():
    """
    Process one manually imported song from original text
    to validated JSON analysis.
    """

    # ------------------ APPLICATION SETUP ------------------

    # Configure logging before any other module begins doing work.
    configure_logging()

    # Load OPENAI_API_KEY and other environment variables.
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("Song Analyzer started.")
    
    ''' ------------------ INPUT file related code ------------------'''

    imported_file = (BASE_DIR / "data" / "imports" / "I walk alone-Tarja.txt")
    logger.info("Starting processing for input file: %s", imported_file)

    original_text = input_read(imported_file)
    if not original_text:
        logger.error("Processing stopped because the input file could not be read.")
        print("Could not read lyrics file.")
        return

    # Extract:
    # line 1 → artist
    # line 2 → song title
    # remaining lines → lyrics
    try:
        song_input = parse_song_input(original_text)
        logger.info("Parsed song input: title='%s', artist='%s'.", song_input.song_title, song_input.artist)

    except ValueError as exc:
        logger.exception("The imported file does not follow the expected structure.")
        print(f"Invalid input: {exc}")
        return
    # ------------------ WEEK AND SONG FOLDER CREATION ------------------

    # Automatically create:  data/<ISO week>/<song>_<artist>_<processing date>/
    song_folder = create_song_folder(artist=song_input.artist, song_title=song_input.song_title )
    logger.info("Created or found song folder: %s", song_folder)


    original_path = song_folder / "original_lyrics.txt"
    cleaned_path = song_folder / "cleaned_lyrics.txt"
    analysis_path = song_folder / "analysis.json"

    # Preserve the manually imported source file.
    save_text(original_path, original_text)

    logger.info("Saved original lyrics to: %s", original_path,)

    # ------------------ INPUT PREPROCESSING ------------------

    # Clean only the lyrics. Artist and song title are metadata and should not be interpreted as emotional evidence.
    cleaned_lyrics = preprocess_text(song_input.lyrics)

    # Give every non-empty lyric line a stable evidence number.
    indexed_lines = create_indexed_lines(cleaned_lyrics)
    numbered_lyrics = format_indexed_lines(indexed_lines)

    # Store the exact cleaned input that will be sent to the LLM.
    save_text(cleaned_path, numbered_lyrics)


    # ------------------ LLM call ------------------ 
    logger.info("Submitting '%s' by '%s' for LLM analysis.", song_input.song_title, song_input.artist)
    raw_output = analyze_lyrics(artist=song_input.artist, song_title=song_input.song_title, clean_text=numbered_lyrics)

    if not raw_output:
        logger.error("The LLM returned no usable response for '%s' by '%s'.", song_input.song_title, song_input.artist)
        print("The LLM analysis failed.")        
        return
    
    logger.info("Received LLM response for '%s' by '%s'.", song_input.song_title, song_input.artist)


    # ------------------ OUTPUT PARSING AND VALIDATION ------------------

    # Convert the raw JSON string into a Python dictionary and
    # validate it against the schema from schema.py.

    parsed_analysis = parse_json(raw_output)

    if parsed_analysis is None:
        logger.error("The LLM response failed JSON parsing or schema validation.")
        print("JSON parsing or schema validation failed.")
        return

    logger.info( "LLM response passed parsing and schema validation.")

  # ------------------ FINAL OUTPUT ------------------

    # Save only the validated structured analysis.
    save_analysis(analysis_path, parsed_analysis)
    logger.info( "Saved validated analysis to: %s", analysis_path)
    logger.info("Song Analyzer completed successfully for '%s' by '%s'.", song_input.song_title, song_input.artist)

    # These are CLI-facing messages, not diagnostic logs.
    print("\nAnalysis completed successfully.")
    print(f"Song: {song_input.song_title}")
    print(f"Artist: {song_input.artist}")
    print(f"Saved analysis: {analysis_path}")

    ''' ------------------ Optional: print nicely ------------------ '''
    print("=== RESULT ===")
    print(json.dumps(parsed_analysis, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
