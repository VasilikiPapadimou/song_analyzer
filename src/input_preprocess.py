import re
from dataclasses import dataclass
from typing import List, Tuple

"""All preprocessing applied to the imported song before it enters the LLM."""

@dataclass(frozen=True)
class SongInput:
    """Structured representation of the manually created input file."""
    artist: str
    song_title: str
    lyrics: str


SECTION_LABEL_PATTERN = re.compile(
    r"""
    ^\s*
    [\[\(\{]?
    (?:
        intro |
        outro |
        verse |
        pre[\s-]?chorus |
        chorus |
        post[\s-]?chorus |
        bridge |
        refrain |
        hook |
        interlude |
        instrumental |
        breakdown |
        solo |
        spoken |
        repeat
    )
    (?:\s+\d+|\s+[ivxlcdm]+)?
    \s*:?
    [\]\)\}]?
    \s*:?\s*
    $
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)

WEBSITE_METADATA_PATTERNS = [
    re.compile(r"^\s*\d+\s*contributors?\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d+(?:\.\d+)?[kmb]?\s+views?\s*$", re.IGNORECASE),
    re.compile(r"^\s*embed\s*$", re.IGNORECASE),
    re.compile(r"^\s*you might also like\s*$", re.IGNORECASE),
    re.compile(r"^\s*translations?\s*$", re.IGNORECASE),
    re.compile(r"^\s*lyrics?\s*$", re.IGNORECASE),
    re.compile(r"^\s*written by\b.*$", re.IGNORECASE),
    re.compile(r"^\s*produced by\b.*$", re.IGNORECASE),
    re.compile(r"^\s*release date\b.*$", re.IGNORECASE),
]


def normalize_line_endings(text: str) -> str:  # converts all line endings to \n
    return text.replace("\r\n", "\n").replace("\r", "\n")

def strip_lines(text: str) -> str:  # Removes spaces at start/end of each line
    return "\n".join(line.strip() for line in text.split("\n"))

def collapse_spaces(text: str) -> str:  # Multiple spaces/tabs → single space
    return re.sub(r"[ \t]+", " ", text)

def remove_extra_empty_lines(text: str) -> str:  # Too many empty lines → max 1 empty line
    return re.sub(r"\n\s*\n+", "\n\n", text)


def parse_song_input(text: str) -> SongInput:
    """
    Extract metadata and lyrics from the imported text file.

    Expected input structure:
    - First line: artist
    - Second line: song title
    - Remaining lines: lyrics
    """
    normalized = normalize_line_endings(text)
    lines = normalized.splitlines()

    if len(lines) < 3:
        raise ValueError("Input must contain artist on line 1, song title on line 2, and lyrics afterward.")

    artist = lines[0].strip()
    song_title = lines[1].strip()
    lyrics = "\n".join(lines[2:]).strip()
    if not artist:
        raise ValueError("Artist on line 1 cannot be empty.")

    if not song_title:
        raise ValueError("Song title on line 2 cannot be empty.")

    if not lyrics:
        raise ValueError("The lyrics section cannot be empty.")

    return SongInput(artist=artist, song_title=song_title, lyrics=lyrics)


def remove_section_labels(text: str) -> (str):  # this removes the labels that might exist in the file naming the parts of a song
    remaining_lines = [line
                       for line in text.splitlines()
                       if not SECTION_LABEL_PATTERN.fullmatch(line)
                       ]
    return "\n".join(remaining_lines)


def remove_website_metadata(text: str) -> (str):  # this removes the metadata that might have been copied from the site when the user
    cleaned_lines = []

    for line in text.splitlines():
        is_metadata = any(
            pattern.fullmatch(line) for pattern in WEBSITE_METADATA_PATTERNS
        )
        if not is_metadata:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


""" -------------------------------- FINAL INPUT RESULT -------------------------------- """


def preprocess_text(text: str, lowercase: bool = False) -> str:
    text = normalize_line_endings(text)
    text = strip_lines(text)
    text = remove_section_labels(text)
    text = remove_website_metadata(text)
    text = collapse_spaces(text)
    text = remove_extra_empty_lines(text)

    if lowercase:
        text = text.lower()

    return text.strip()


# Numbering of lines in lyrics
def create_indexed_lines(text: str) -> List[Tuple[int, str]]:
    lines = text.split("\n")
    indexed = []
    line_number = 1

    for line in lines:
        if line.strip():  # skip empty lines
            indexed.append((line_number, line))
            line_number += 1

    return indexed

def format_indexed_lines(indexed_lines: List[Tuple[int, str]]) -> str:
    return "\n".join(
        f"[{line_number}] {line}"
        for line_number, line in indexed_lines
    )

def add_line_numbers(text: str) -> str:
    indexed_lines = create_indexed_lines(text)

    return "\n".join(f"[{line_number}] {line}" for line_number, line in indexed_lines)
