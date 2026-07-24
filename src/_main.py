from dotenv import load_dotenv
import os
from file_manager import BASE_DIR,ensure_output_dirs,input_read,save_raw_output,save_parsed_output
from input_preprocess import preprocess_text
from analyzer import analyze_lyrics
import json
from parser import parse_json


def main():
    ''' ------------------ INPUT file related code ------------------'''
    load_dotenv()
    ensure_output_dirs()
    file_path = BASE_DIR / "data" / "songs" / "Warrior-Aurora.txt"
    lyrics = input_read(file_path)  
    if not lyrics:
        print("Could not read lyrics file.")
        return
    clean_lyrics = preprocess_text(lyrics) # Preprocessing: clean up lyrics

    song_name = os.path.splitext(os.path.basename(file_path))[0]    # Extract song name from txt

    ''' ------------------ LLM call + OUTPUT related code ------------------
        1. After preprocessing the lyrics pass through the LLM (API Call) and the 1st output is the RAW output
        2. Then the RAW OUTPUT is saved to output/raw/song_rawjson.txt
        3. This RAW OUTPUT is :
            - structured as per the given schema --> schema.py  
            - validated as PARSED OUTPUT via code and not by the LLM --> parser.py 
        4. The PARSED OUTPUT is saved by 2_file_manager.py and is saved in output/parsed/song_parsed.json and prints it in the CLI 

    '''
    raw_output = analyze_lyrics(clean_lyrics)  # 1️⃣ Call LLM (returns RAW string now)
    if not raw_output:
        print("❌ LLM failed")
        return
    save_raw_output(song_name, raw_output)    # 2️⃣ Save RAW

    parsed = parse_json(raw_output)    # 3️⃣ Parse JSON
    if parsed is None:
        print("❌ JSON parsing or schema validation failed")
        return
    save_parsed_output(song_name, parsed)     # 4️⃣ Save PARSED JSON

    ''' ------------------ Optional: print nicely ------------------ '''
    print("=== RESULT ===")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
