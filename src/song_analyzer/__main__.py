from dotenv import load_dotenv

from song_analyzer.config import BASE_DIR, configure_logging
from song_analyzer.pipeline import run_pipeline


def main() -> None:
    configure_logging()
    load_dotenv()

    input_path = BASE_DIR / "data" / "imports" / "example_song.txt"

    run_pipeline(input_path)


if __name__ == "__main__":
    main()