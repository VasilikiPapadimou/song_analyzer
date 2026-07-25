from datetime import datetime
from pathlib import Path
import json
import logging
import re

""" 
    This is where we will have everything related to:
        - path creation, 
        - input text file creation/open/save
        - output text file creation and 
        - parsed json file in dict format

"""
# points to "/song_analyzer/data" (project root)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"/ "exports"

logger = logging.getLogger(__name__)


def input_read(file_path: Path) -> str:
    try:
        content = file_path.read_text(encoding="utf-8")
        logger.info("Successfully read input file: %s", file_path)
        return content
        
    except FileNotFoundError:
        logger.error("Input file was not found: %s ", file_path)
        return ""
    except UnicodeDecodeError:
        logger.error("Input file is not valid UTF-8: %s", file_path)
        return ""
    except OSError:
        logger.error( "Could not read input file: %s", file_path)
        return ""

"""
--------------------------Output processing--------------------------
    1.Filepath creation:
      - Add ISO-week helper
      - Safe-folder helper : lowercase and normalization of path
      - Create week_folder-song_folder structure 
    2. Add/Create text output
    3. Create and save json output 
"""
def get_current_week_id(processed_at: datetime | None = None) -> str:
    current = processed_at or datetime.now()
    iso_year, iso_week, _ = current.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def make_path_safe(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "_", value)
    return value.strip("_")


def create_song_folder(artist: str, song_title: str, processed_at: datetime | None = None) -> Path:
    # week folder creation
    current = processed_at or datetime.now()
    week_id = get_current_week_id(current)
    date_part = current.strftime("%Y-%m-%d")

    # song folder creation
    song_folder_name = (f"{make_path_safe(song_title)}_{make_path_safe(artist)}_{date_part}")

    # week+songfolder = directory creation
    song_folder = DATA_DIR / week_id / song_folder_name
    song_folder.mkdir(parents=True, exist_ok=True)

    return song_folder


""" -------------------------- Output text + Parsed json -------------------------- """


def save_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def save_analysis(path: Path, analysis: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return path
