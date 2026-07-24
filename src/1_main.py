from dotenv import load_dotenv
import os
from file_manager import BASE_DIR,ensure_output_dirs,input_read,save_raw_output,save_parsed_output
from input_preprocess import preprocess_text
from analyzer import analyze_lyrics
import json
from parser import parse_json


def main():
    load_dotenv()
    ensure_output_dirs()
    file_path = BASE_DIR / "data" / "songs" / "Warrior-Aurora.txt"

    lyrics = input_read(file_path)    #get the lyrics from the data\songs file
    if not lyrics:
        print("Could not read lyrics file.")
        return

    clean_lyrics = preprocess_text(lyrics) # perform the clean up of the lyrics
    
 # Extract song name from file
    song_name = os.path.splitext(os.path.basename(file_path))[0]

    # 1️⃣ Call LLM (returns RAW string now)
    raw_output = analyze_lyrics(clean_lyrics)
    if not raw_output:
        print("❌ LLM failed")
        return
    # 2️⃣ Save RAW
    save_raw_output(song_name, raw_output)

    # 3️⃣ Parse JSON
    parsed = parse_json(raw_output)

    if parsed is None:
        print("❌ JSON parsing or schema validation failed")
        return

    # 4️⃣ Save PARSED JSON
    save_parsed_output(song_name, parsed)

    # Optional: print nicely
    print("=== RESULT ===")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
