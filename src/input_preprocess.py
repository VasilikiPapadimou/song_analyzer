import re
from typing import List, Tuple


def normalize_line_endings(text: str) -> str:  # converts all line endings to \n
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_lines(text: str) -> str:  # Removes spaces at start/end of each line
    return "\n".join(line.strip() for line in text.split("\n"))


def collapse_spaces(text: str) -> str:  # Multiple spaces/tabs → single space
    return re.sub(r"[ \t]+", " ", text)


# Too many empty lines → max 1 empty line
def remove_extra_empty_lines(text: str) -> str:
    return re.sub(r"\n\s*\n+", "\n\n", text)


def preprocess_text(text: str, lowercase: bool = False) -> str:
    text = normalize_line_endings(text)
    text = strip_lines(text)
    text = collapse_spaces(text)
    text = remove_extra_empty_lines(text)

    if lowercase:
        text = text.lower()

    return text.strip()


# metadata version (no pollution of main text)
def create_indexed_lines(text: str) -> List[Tuple[int, str]]:
    lines = text.split("\n")

    indexed = []
    line_number = 1

    for line in lines:
        if line.strip():  # skip empty lines
            indexed.append((line_number, line))
            line_number += 1

    return indexed
