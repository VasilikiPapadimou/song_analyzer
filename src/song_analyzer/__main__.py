from dotenv import load_dotenv

from song_analyzer.config import configure_logging
from song_analyzer.pipeline import run_pipeline


def main() -> None:
    configure_logging()
    load_dotenv()

    run_pipeline()


if __name__ == "__main__":
    main()