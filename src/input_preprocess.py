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

# -------------------------------------------------------------------
# SECTION LABEL DETECTION
# -------------------------------------------------------------------

SECTION_TYPES = r"""
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
"""

SECTION_BODY_PATTERN = re.compile(
    rf"""
    ^\s*
    (?:{SECTION_TYPES})
    (?:\s+(?:\d+|[ivxlcdm]+))?
    (?:\s*:\s*.+)?
    \s*$
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)

BRACKET_PAIRS = {
    "[": "]",
    "(": ")",
    "{": "}"
}

PLAIN_SECTION_PATTERN = re.compile(
    rf"""
    ^\s*
    (?:{SECTION_TYPES})
    (?:\s+(?:\d+|[ivxlcdm]+))?
    \s*:?
    \s*$
    """,
    flags=re.IGNORECASE | re.VERBOSE
)

# -------------------------------------------------------------------
# WEBSITE METADATA
# -------------------------------------------------------------------

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


'''--------------------------------PART:A -> NORMALIZE & INPUT PARSING ORIGINAL FILE--------------------------------'''

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


'''-------------------------------------PART B -> REMOVE METADATA & LABELS -------------------------------------'''

def is_section_label(line: str) -> bool: 
    '''Determines whether a lyric line represents structural song metadata '''
    stripped = line.strip()
    if not stripped:
        return False
        
    if len(stripped) >= 2:
        opening_bracket = stripped[0]
        closing_bracket = stripped[-1]

        if (opening_bracket in BRACKET_PAIRS and BRACKET_PAIRS[opening_bracket] == closing_bracket):
            inner_text = stripped[1:-1].strip()

            return bool(SECTION_BODY_PATTERN.fullmatch(inner_text))

    return bool(PLAIN_SECTION_PATTERN.fullmatch(stripped))


def remove_section_labels(text: str) -> (str):  
    """
        Remove structural section labels while preserving actual lyric lines.
    """ 
    remaining_lines = [line
                       for line in text.splitlines()
                       if not is_section_label(line)
                       ]
    return "\n".join(remaining_lines)

# -------------------------------------------------------------------
# WEBSITE METADATA REMOVAL
# -------------------------------------------------------------------

def remove_website_metadata(text: str) -> (str):  # this removes the metadata that might have been copied from the site when the user
    cleaned_lines = []

    for line in text.splitlines():
        is_metadata = any(
            pattern.fullmatch(line) for pattern in WEBSITE_METADATA_PATTERNS
        )
        if not is_metadata:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


""" --------------------------------PART C -> OUTPUT CLEAN LYRICS-------------------------------- """

def preprocess_text(text: str, lowercase: bool = False) -> str:
    """
    Apply all preprocessing steps before lyrics are sent to the LLM.
    """
    text = normalize_line_endings(text)
    text = strip_lines(text)
    text = remove_section_labels(text)
    text = remove_website_metadata(text)
    text = collapse_spaces(text)
    text = remove_extra_empty_lines(text)

    if lowercase:
        text = text.lower()

    return text.strip()


''' --------------------------------PART D -> NUMBERED LYRICS CONTENT--------------------------------'''

def create_indexed_lines(text: str) -> List[Tuple[int, str]]:
    """
        Assign sequential numbers to non-empty lyric lines.

        Empty lines are ignored.
    """
    lines = text.split("\n")
    indexed = []
    line_number = 1

    for line in lines:
        if line.strip():  # skip empty lines
            indexed.append((line_number, line))
            line_number += 1

    return indexed

def format_indexed_lines(indexed_lines: List[Tuple[int, str]]) -> str:
    """
        Convert indexed lyric lines into the format expected by the LLM.
    """

    return "\n".join(
        f"[{line_number}] {line}"
        for line_number, line in indexed_lines
    )

def add_line_numbers(text: str) -> str:
    indexed_lines = create_indexed_lines(text)

    return "\n".join(f"[{line_number}] {line}" for line_number, line in indexed_lines)
