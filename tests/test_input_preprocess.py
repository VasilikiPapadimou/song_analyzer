"""Tests for song input parsing and lyrics preprocessing."""

import pytest

from song_analyzer.input_preprocess import (
    add_line_numbers,
    create_indexed_lines,
    format_indexed_lines,
    is_section_label,
    normalize_line_endings,
    parse_song_input,
    preprocess_text,
    remove_section_labels,
    remove_website_metadata,
 )


# ------------------ PART A: INPUT PARSING ------------------

def test_valid_input() -> None:
    """Artist, title, and lyrics should be extracted from the expected lines."""

    text = (
        "Linkin Park\n"
        "In the End\n"
        "It starts with one\n"
        "One thing, I don't know why"
    )

    result = parse_song_input(text)

    assert result.artist == "Linkin Park"
    assert result.song_title == "In the End"
    assert result.lyrics == (
        "It starts with one\n"
        "One thing, I don't know why"
    )


def test_windows_newlines() -> None:
    """Windows line endings should not affect song input parsing."""

    text = (
        "Linkin Park\r\n"
        "In the End\r\n"
        "It starts with one\r\n"
        "One thing, I don't know why"
    )

    result = parse_song_input(text)

    assert result.artist == "Linkin Park"
    assert result.song_title == "In the End"
    assert result.lyrics == (
        "It starts with one\n"
        "One thing, I don't know why"
    )


def test_missing_artist() -> None:
    """An empty artist line should make the input invalid."""

    text = (
        "\n"
        "In the End\n"
        "It starts with one"
    )

    with pytest.raises(
        ValueError,
        match="Artist on line 1 cannot be empty",
    ):
        parse_song_input(text)


def test_missing_title() -> None:
    """An empty song-title line should make the input invalid."""

    text = (
        "Linkin Park\n"
        "\n"
        "It starts with one"
    )

    with pytest.raises(
        ValueError,
        match="Song title on line 2 cannot be empty",
    ):
        parse_song_input(text)


def test_missing_lyrics() -> None:
    """An input without lyrics should not continue to the LLM pipeline."""

    text = (
        "Linkin Park\n"
        "In the End\n"
        "   "
    )

    with pytest.raises(
        ValueError,
        match="The lyrics section cannot be empty",
    ):
        parse_song_input(text)

def test_too_few_lines() -> None:
    """Artist and title alone are not enough; lyrics must follow."""

    text = (
        "Linkin Park\n"
        "In the End"
    )

    with pytest.raises(ValueError, match="Input must contain artist on line 1, song title on line 2, and lyrics afterward",):
        parse_song_input(text)

def test_strip_input_spaces() -> None:
    """Extra spaces around metadata and lyrics should be removed."""

    text = (
        "  Linkin Park  \n"
        "  In the End  \n"
        "  It starts with one  "
    )

    result = parse_song_input(text)

    assert result.artist == "Linkin Park"
    assert result.song_title == "In the End"
    assert result.lyrics == "It starts with one"

def test_carriage_returns() -> None:
    """Old-style carriage-return line endings should become newline characters."""

    text = "Line one\rLine two\rLine three"

    result = normalize_line_endings(text)

    assert result == "Line one\nLine two\nLine three"

# ------------------ PART B: METADATA REMOVAL ------------------

def test_bracketed_labels() -> None:
    """Bracketed section labels should be removed."""

    text = (
        "[Verse 1]\n"
        "It starts with one\n"
        "[Chorus]\n"
        "I tried so hard"
    )

    result = remove_section_labels(text)

    assert result == (
        "It starts with one\n"
        "I tried so hard"
    )


def test_plain_labels() -> None:
    """Plain section labels should be removed."""

    text = (
        "Verse 1\n"
        "It starts with one\n"
        "Chorus:\n"
        "I tried so hard"
    )

    result = remove_section_labels(text)

    assert result == (
        "It starts with one\n"
        "I tried so hard"
    )


def test_detailed_label() -> None:
    """Section labels containing extra description should be removed."""

    text = (
        "[Chorus: Mike Shinoda]\n"
        "I tried so hard"
    )

    result = remove_section_labels(text)

    assert result == "I tried so hard"


def test_real_lyrics_preserved() -> None:
    """Normal lyric lines containing section words should remain."""

    text = (
        "This chorus keeps playing in my head\n"
        "I tried so hard"
    )

    result = remove_section_labels(text)

    assert result == text


def test_website_metadata() -> None:
    """Common website metadata should be removed."""

    text = (
        "12 Contributors\n"
        "2.5K Views\n"
        "Embed\n"
        "You Might Also Like\n"
        "Lyrics\n"
        "Written by Mike Shinoda\n"
        "Produced by Don Gilmore\n"
        "Release Date October 24, 2000\n"
        "It starts with one"
    )

    result = remove_website_metadata(text)

    assert result == "It starts with one"

def test_section_label_detection() -> None:
    """Section labels should be detected without matching normal lyric lines."""

    assert is_section_label("[Verse 1]") is True
    assert is_section_label("Chorus") is True
    assert is_section_label("(Bridge)") is True
    assert is_section_label("[Chorus: Mike Shinoda]") is True

    assert is_section_label("This chorus keeps playing in my head") is False
    assert is_section_label("I am standing on a bridge") is False
    assert is_section_label("") is False
    # ------------------ PART C: FULL PREPROCESSING ------------------

def test_full_preprocessing() -> None:
    """The complete preprocessing pipeline should clean lyrics correctly."""

    text = (
        "[Verse 1]\r\n"
        "  It   starts with one  \r\n"
        "\r\n"
        "\r\n"
        "2.5K Views\r\n"
        "[Chorus]\r\n"
        "  I   tried so hard  "
    )

    result = preprocess_text(text)

    assert result == (
        "It starts with one\n"
        "\n"
        "I tried so hard"
    )


def test_case_preserved() -> None:
    """Letter casing should remain unchanged by default."""

    text = "I TRIED So Hard"

    result = preprocess_text(text)

    assert result == "I TRIED So Hard"


def test_lowercase_option() -> None:
    """Lyrics should be converted to lowercase when requested."""

    text = "I TRIED So Hard"

    result = preprocess_text(text, lowercase=True)

    assert result == "i tried so hard"

# ------------------ PART D: LINE NUMBERING ------------------

def test_index_lines() -> None:
    """Lyric lines should receive sequential numbers."""

    text = (
        "It starts with one\n"
        "I tried so hard\n"
        "But in the end"
    )

    result = create_indexed_lines(text)

    assert result == [
        (1, "It starts with one"),
        (2, "I tried so hard"),
        (3, "But in the end"),
    ]


def test_skip_empty_lines() -> None:
    """Empty lyric lines should not receive line numbers."""

    text = (
        "It starts with one\n"
        "\n"
        "   \n"
        "I tried so hard"
    )

    result = create_indexed_lines(text)

    assert result == [
        (1, "It starts with one"),
        (2, "I tried so hard"),
    ]


def test_format_lines() -> None:
    """Indexed lyrics should use the format expected by the LLM."""

    indexed = [
        (1, "It starts with one"),
        (2, "I tried so hard"),
    ]

    result = format_indexed_lines(indexed)

    assert result == (
        "[1] It starts with one\n"
        "[2] I tried so hard"
    )


def test_add_line_numbers() -> None:
    """Line numbering should work directly from lyric text."""

    text = (
        "It starts with one\n"
        "\n"
        "I tried so hard"
    )

    result = add_line_numbers(text)

    assert result == (
        "[1] It starts with one\n"
        "[2] I tried so hard"
    )


def test_empty_text_numbering() -> None:
    """Empty lyric text should produce no numbered lines."""

    assert create_indexed_lines("") == []
    assert add_line_numbers("") == ""# ------------------ PART D: LINE NUMBERING ------------------

def test_index_lines() -> None:
    """Lyric lines should receive sequential numbers."""

    text = (
        "It starts with one\n"
        "I tried so hard\n"
        "But in the end"
    )

    result = create_indexed_lines(text)

    assert result == [
        (1, "It starts with one"),
        (2, "I tried so hard"),
        (3, "But in the end"),
    ]


def test_skip_empty_lines() -> None:
    """Empty lyric lines should not receive line numbers."""

    text = (
        "It starts with one\n"
        "\n"
        "   \n"
        "I tried so hard"
    )

    result = create_indexed_lines(text)

    assert result == [
        (1, "It starts with one"),
        (2, "I tried so hard"),
    ]


def test_format_lines() -> None:
    """Indexed lyrics should use the format expected by the LLM."""

    indexed = [
        (1, "It starts with one"),
        (2, "I tried so hard"),
    ]

    result = format_indexed_lines(indexed)

    assert result == (
        "[1] It starts with one\n"
        "[2] I tried so hard"
    )


def test_add_line_numbers() -> None:
    """Line numbering should work directly from lyric text."""

    text = (
        "It starts with one\n"
        "\n"
        "I tried so hard"
    )

    result = add_line_numbers(text)

    assert result == (
        "[1] It starts with one\n"
        "[2] I tried so hard"
    )


def test_empty_text_numbering() -> None:
    """Empty lyric text should produce no numbered lines."""

    assert create_indexed_lines("") == []
    assert add_line_numbers("") == ""