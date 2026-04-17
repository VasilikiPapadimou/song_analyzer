from dotenv import load_dotenv
from file_manager import input_read
from input_preprocess import preprocess_text
from analyzer import analyze_lyrics
import json


def main():
    load_dotenv()

    lyrics = input_read("data/songs/Warrior-Aurora.txt")
    if not lyrics:
        print("Could not read lyrics file.")
        return

    clean_lyrics = preprocess_text(lyrics)

    result = analyze_lyrics(clean_lyrics)

    print("=== RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
