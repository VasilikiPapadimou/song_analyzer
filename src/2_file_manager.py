from datetime import datetime
import os
import logging
import json
from pathlib import Path

# points to /song_analyzer (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)

def input_read(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as song_lyrics:
            return song_lyrics.read()

    except FileNotFoundError as fde:
        logging.error(f"File not found: {file_path} | {fde}")
        return ""
    except Exception as e:
        logging.error(f"Failed to rosead {file_path}: {e}")
        return ""

#--------------------------Output processing--------------------------#
'''
The filename inside the output raw file will be the json in python dictionary format (parsed)
the filename will 
'''
def ensure_output_dirs():
    os.makedirs("output/raw", exist_ok=True)
    os.makedirs("output/parsed", exist_ok=True)

# Generate output filename
def generate_filename(song_name: str, suffix: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    return f"{song_name}_{date}_{suffix}"

# Save RAW output txt file
def save_raw_output(song_name: str, raw_content: str) -> str:
    filename = generate_filename(song_name, "raw.txt")
    path = os.path.join("output", "raw", filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(raw_content)

    return path

# Save PARSED JSON dict format
def save_parsed_output(song_name: str, parsed_data: dict) -> str:
    filename = generate_filename(song_name, "parsed.json")
    path = os.path.join("output", "parsed", filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)

    return path
