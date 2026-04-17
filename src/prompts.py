def build_prompt(clean_text: str) -> str:
    return f"""
You are analyzing song lyrics.

Your job:
- infer the meaning of the song from the lyrics only
- stay grounded in the text
- do not invent facts outside the lyrics
- keep the summary concise but meaningful
- use evidence lines only when they genuinely support the interpretation
- if something is ambiguous, mention it in uncertainty_notes

Important:
- The first line of the lyrics is the song title
- The second line of the lyrics is the artist
- Return the result in the required structured format

Lyrics:
{clean_text}
""".strip()
