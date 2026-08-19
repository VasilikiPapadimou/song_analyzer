"""
Prompt construction for the first Song Analyzer LLM call.

The prompt defines how the lyrics should be interpreted.
The JSON structure itself is enforced by SONG_ANALYSIS_SCHEMA.
"""

from song_analyzer.schemas.taxonomies import (AGENCY_LEVELS, ARC_MOVEMENTS, CONFIDENCE_LEVELS, EMOTION_FAMILIES, EMOTION_ROLES, RESOLUTION_STATES, THEME_FAMILIES, THEME_ROLES)


PROMPT_VERSION = "2.0"


def format_allowed_values(values: list[str]) -> str:
    """Convert a taxonomy list into a prompt-friendly string."""
    return ", ".join(values)


def build_prompt(artist: str, song_title: str, clean_text: str) -> str:
    """
    Build the prompt used for the first lyrics-analysis LLM call.

    The artist and song title provide context but are not returned by
    the LLM. They will later be added to metadata by Python.
    """

    return f"""
You are a music lyrics analysis system.

Analyze only the supplied numbered lyrics.

Song context:
- Artist: {artist}
- Song title: {song_title}

The JSON structure is enforced separately by a JSON schema.
Your task is to populate its fields accurately and consistently.

THEMES

Identify only clearly supported themes.

For each theme:
- family must be one of:
  {format_allowed_values(THEME_FAMILIES)}
- label must briefly describe the specific form of the theme.
- role must be one of:
  {format_allowed_values(THEME_ROLES)}
- evidence_line_numbers must contain the numbered lyric lines that
  directly support the theme.

Use "primary" only for themes central to the song.
Use "secondary" for meaningful but less central themes.

EMOTIONS

Identify only emotions clearly expressed or strongly implied by the
lyrics.

For each emotion:
- family must be one of:
  {format_allowed_values(EMOTION_FAMILIES)}
- label must name the specific emotional form, such as melancholy,
  grief, tenderness, dread, or resilience.
- role must be one of:
  {format_allowed_values(EMOTION_ROLES)}
- intensity must use this scale:
  1 = faint
  2 = mild
  3 = clear and moderate
  4 = strong
  5 = dominant and pervasive
- evidence_line_numbers must directly support that emotion.

Use family as the normalized category and label as the more precise
description.

EMOTIONAL ARC

Describe how the emotional state changes through the lyrics.

- starting_state must describe the emotion present near the beginning.
- turning_points must contain only clear emotional transitions.
  Return an empty list when no clear turning point exists.
- ending_state must describe the emotion present near the ending.
- overall_movement must be one of:
  {format_allowed_values(ARC_MOVEMENTS)}

Each emotional state and turning point must use valid emotion families
and supporting lyric line numbers.

AGENCY LEVEL

Assess how much ability, intention, or control the narrator expresses.

- level must be one of:
  {format_allowed_values(AGENCY_LEVELS)}
- evidence_line_numbers must support the selected level.

Use:
- low for helplessness or passivity
- medium for limited or hesitant action
- high for clear choice, action, or self-direction
- mixed when active and passive positions coexist
- ambiguous when the lyrics do not support a stable conclusion

RESOLUTION STATE

Assess whether the main emotional or thematic conflict reaches closure.

- status must be one of:
  {format_allowed_values(RESOLUTION_STATES)}
- evidence_line_numbers must support the selected status.

Use:
- resolved for clear closure, acceptance, or decision
- partially_resolved for meaningful movement without full closure
- unresolved when the conflict remains open
- ambiguous when the ending supports multiple interpretations

UNCERTAINTY

- confidence_level must be one of:
  {format_allowed_values(CONFIDENCE_LEVELS)}
- use high when the important observations are directly supported
- use medium when the main analysis is supported but meaningful
  ambiguity remains
- use low when several conclusions depend on uncertain interpretation
- flagged_fields must identify any specific analytical fields affected
  by meaningful uncertainty
- return an empty flagged_fields list when no field requires a warning

GROUNDING RULES

- Use only information contained in the supplied lyrics.
- Use only line numbers that appear in the numbered lyrics.
- Do not invent lyric evidence.
- Do not use the artist name or song title as evidence.
- Do not infer the artist's biography, intentions, or mental health.
- Do not infer the listener's or user's psychological state.
- Do not make clinical or diagnostic claims.
- Prefer "ambiguous" over an unsupported conclusion.
- Keep labels and uncertainty reasons concise.
- Return only the JSON required by the provided schema.

Numbered lyrics:

{clean_text}
""".strip()