from dotenv import load_dotenv
import json
from file_manager import ( BASE_DIR, create_song_folder, input_read, save_analysis, save_text)
from input_preprocess import (create_indexed_lines, format_indexed_lines, parse_song_input, preprocess_text)
from API_LyricsAnalyzer import analyze_lyrics
from parser import parse_json
from config import configure_logging
import logging

def main():
   # Configure terminal and persistent file logging.
    configure_logging()
    # Load variables such as OPENAI_API_KEY from .env.
    load_dotenv()
    
    ''' ------------------ INPUT file related code ------------------'''

    imported_file = (BASE_DIR / "data" / "imports" / "I walk alone-Tarja.txt")

    logger = logging.getLogger(__name__)
    logger.info("Starting processing for input file: %s", imported_file)

    original_text = input_read(imported_file)
    if not original_text:
        print("Could not read lyrics file.")
        return

    try:
        song_input = parse_song_input(original_text) 
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        return

    song_folder = create_song_folder(artist=song_input.artist, song_title=song_input.song_title )

    original_path = song_folder / "original_lyrics.txt"
    cleaned_path = song_folder / "cleaned_lyrics.txt"
    analysis_path = song_folder / "analysis.json"

    save_text(original_path, original_text) 
    cleaned_lyrics = preprocess_text(song_input.lyrics)
    indexed_lines = create_indexed_lines(cleaned_lyrics)
    numbered_lyrics = format_indexed_lines(indexed_lines)

    save_text(cleaned_path, numbered_lyrics)

    ''' ------------------ LLM call + OUTPUT related code ------------------
        1. After preprocessing the lyrics pass through the LLM (API Call) and the 1st output is the RAW output
        2. Then the RAW OUTPUT is saved to output/raw/song_rawjson.txt
        3. This RAW OUTPUT is :
            - structured as per the given schema --> schema.py  
            - validated as PARSED OUTPUT via code and not by the LLM --> parser.py 
        4. The PARSED OUTPUT is saved by 2_file_manager.py and is saved in output/parsed/song_parsed.json and prints it in the CLI 

    '''
    raw_output = analyze_lyrics(artist=song_input.artist, song_title=song_input.song_title, clean_text=numbered_lyrics)

    if not raw_output:
        print("LLM failed.")
        return

    parsed = parse_json(raw_output)

    if parsed is None:
        failed_response_path = song_folder / "failed_raw_response.txt"
        save_text(failed_response_path, raw_output)

        print("JSON parsing or schema validation failed.")
        return

    save_analysis(analysis_path, parsed)

    ''' ------------------ Optional: print nicely ------------------ '''
    print("=== RESULT ===")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
