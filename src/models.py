SONG_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "song_title": {"type": "string"},
        "artist": {"type": "string"},
        "interpretation_summary": {"type": "string"},
        "dominant_emotions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "emotional_arc": {"type": "string"},
        "narrator_perspective": {"type": "string"},
        "key_evidence_lines": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "line_number": {"type": "integer"},
                    "text": {"type": "string"}
                },
                "required": ["line_number", "text"]
            }
        },
        "uncertainty_notes": {"type": "string"}
    },
    "required": [
        "song_title",
        "artist",
        "interpretation_summary",
        "dominant_emotions",
        "emotional_arc",
        "narrator_perspective",
        "key_evidence_lines",
        "uncertainty_notes"
    ]
}
