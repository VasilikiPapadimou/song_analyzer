import logging
from pathlib import Path


LLM_MODEL = "gpt-4o-mini"

# Project root: song_analyzer/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Persistent application logs are stored here.
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Logs are written both to:
    - logs/app.log
    - the terminal
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )