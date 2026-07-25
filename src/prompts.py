def build_prompt(artist: str, song_title: str, clean_text: str) -> str:
    return f"""
      You are a music analysis assistant.

      Song metadata:
      - Artist: {artist}
      - Song title: {song_title}

      Analyze the numbered lyrics below.

      Your analysis should include:
      - song_title: Use the supplied song title exactly.
      - artist: Use the supplied artist exactly.
      - interpretation_summary: Provide densely the meaning of the song's and themes .
      - dominant_emotions: A list of the main emotions conveyed.
      - key_evidence_lines: Relevant lyric lines and their supplied line numbers when they describe a dominant emotion.
      - emotional_arc: How the emotions evolve through the song.
      - narrator_perspective: The narrative point of view.
      - uncertainty_notes: Ambiguities or limits in the interpretation. (e.g., poetic language, metaphors, cultural references that may have multiple meanings etc)

      Important rules:
      - Return the required JSON structure.
      - Stay grounded in the supplied lyrics.
      - Do not infer a different title or artist.
      - Use only the supplied line numbers.
      - Do not invent evidence lines.

      Numbered lyrics:{clean_text}
""".strip()