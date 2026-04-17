import os
import logging

logger = logging.getLogger(__name__)


def input_read(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as song_lyrics:
            return song_lyrics.read()

    except FileNotFoundError as fde:
        logging.error(f"File not found: {file_path} | {fde}")
        return ""
    except Exception as e:
        logging.error(f"Failed to read {file_path}: {e}")
        return ""


def preprocess(text: str) -> str:
    if not text:
        return ""

    # 1. Remove empty lines
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    text = "\n".join(lines)

    # 2. Normalize spaces
    text = " ".join(text.split())

    # 3. Remove repeated words
    words = text.split()
    cleaned = []

    for word in words:
        if not cleaned or word != cleaned[-1]:
            cleaned.append(word)

    text = " ".join(cleaned)

    return text
