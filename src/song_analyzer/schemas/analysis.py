"""
JSON schemas used by the Song Analyzer processing stage.

SONG_ANALYSIS_SCHEMA
    Defines the structured output returned by the first LLM call.

FINAL_ANALYSIS_SCHEMA
    Defines the complete analysis.json file after deterministic
    metadata has been added by the application.
"""

SCHEMA_VERSION = "2.0"

from song_analyzer.schemas.taxonomies import (
    AGENCY_LEVELS,
    ARC_MOVEMENTS,
    CONFIDENCE_LEVELS,
    EMOTION_FAMILIES,
    EMOTION_ROLES,
    RESOLUTION_STATES,
    THEME_FAMILIES,
    THEME_ROLES,
    UNCERTAINTY_FIELDS,
)

# -------------------------------------------------------------------
# REUSABLE SUB-SCHEMAS
# -------------------------------------------------------------------

EVIDENCE_LINE_NUMBERS_SCHEMA = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "integer",
        "minimum": 1,
    },
}


EMOTIONAL_STATE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "emotion_family": {
            "type": "string",
            "enum": EMOTION_FAMILIES,
        },
        "label": {
            "type": "string",
        },
        "evidence_line_numbers": EVIDENCE_LINE_NUMBERS_SCHEMA,
    },
    "required": [
        "emotion_family",
        "label",
        "evidence_line_numbers",
    ],
}


# -------------------------------------------------------------------
# LYRICS ANALYSIS
# -------------------------------------------------------------------

LYRICS_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "themes": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "family": {
                        "type": "string",
                        "enum": THEME_FAMILIES,
                    },
                    "label": {
                        "type": "string",
                    },
                    "role": {
                        "type": "string",
                        "enum": THEME_ROLES,
                    },
                    "evidence_line_numbers": (
                        EVIDENCE_LINE_NUMBERS_SCHEMA
                    ),
                },
                "required": [
                    "family",
                    "label",
                    "role",
                    "evidence_line_numbers",
                ],
            },
        },

        "emotions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "family": {
                        "type": "string",
                        "enum": EMOTION_FAMILIES,
                    },
                    "label": {
                        "type": "string",
                    },
                    "role": {
                        "type": "string",
                        "enum": EMOTION_ROLES,
                    },
                    "intensity": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                    },
                    "evidence_line_numbers": (
                        EVIDENCE_LINE_NUMBERS_SCHEMA
                    ),
                },
                "required": [
                    "family",
                    "label",
                    "role",
                    "intensity",
                    "evidence_line_numbers",
                ],
            },
        },

        "emotional_arc": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "starting_state": EMOTIONAL_STATE_SCHEMA,
                "turning_points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "from_family": {
                                "type": "string",
                                "enum": EMOTION_FAMILIES,
                            },
                            "to_family": {
                                "type": "string",
                                "enum": EMOTION_FAMILIES,
                            },
                            "evidence_line_numbers": (
                                EVIDENCE_LINE_NUMBERS_SCHEMA
                            ),
                        },
                        "required": [
                            "from_family",
                            "to_family",
                            "evidence_line_numbers",
                        ],
                    },
                },

                "ending_state": EMOTIONAL_STATE_SCHEMA,

                "overall_movement": {
                    "type": "string",
                    "enum": ARC_MOVEMENTS,
                },
            },
            "required": [
                "starting_state",
                "turning_points",
                "ending_state",
                "overall_movement",
            ],
        },
        "agency_level": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "level": {
                    "type": "string",
                    "enum": AGENCY_LEVELS,
                },
                "evidence_line_numbers": (
                    EVIDENCE_LINE_NUMBERS_SCHEMA
                ),
            },
            "required": [
                "level",
                "evidence_line_numbers",
            ],
        },

        "resolution_state": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "status": {
                    "type": "string",
                    "enum": RESOLUTION_STATES,
                },
                "evidence_line_numbers": (
                    EVIDENCE_LINE_NUMBERS_SCHEMA
                ),
            },
            "required": [
                "status",
                "evidence_line_numbers",
            ],
        },
    },
    "required": [
        "themes",
        "emotions",
        "emotional_arc",
        "agency_level",
        "resolution_state",
    ],
}


# -------------------------------------------------------------------
# UNCERTAINTY
# -------------------------------------------------------------------

UNCERTAINTY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "confidence_level": {
            "type": "string",
            "enum": CONFIDENCE_LEVELS,
        },

        "flagged_fields": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "field": {
                        "type": "string",
                        "enum": UNCERTAINTY_FIELDS,
                    },
                    "reason": {
                        "type": "string",
                    },
                },
                "required": [
                    "field",
                    "reason",
                ],
            },
        },
    },
    "required": [
        "confidence_level",
        "flagged_fields",
    ],
}


# -------------------------------------------------------------------
# FIRST LLM CALL OUTPUT
# -------------------------------------------------------------------

SONG_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "lyrics_analysis": LYRICS_ANALYSIS_SCHEMA,
        "uncertainty": UNCERTAINTY_SCHEMA,
    },
    "required": [
        "lyrics_analysis",
        "uncertainty",
    ],
}


# -------------------------------------------------------------------
# FINAL ANALYSIS.JSON METADATA
# -------------------------------------------------------------------

METADATA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {
            "type": "string",
            "const": SCHEMA_VERSION,
        },
        "song_title": {
            "type": "string",
        },
        "artist": {
            "type": "string",
        },
        "processed_at": {
            "type": "string",
        },
        "model": {
            "type": "string",
        },
        "prompt_version": {
            "type": "string",
        },
    },
    "required": [
        "schema_version",
        "song_title",
        "artist",
        "processed_at",
        "model",
        "prompt_version",
    ],
}


# -------------------------------------------------------------------
# FINAL ANALYSIS.JSON CONTRACT
# -------------------------------------------------------------------

FINAL_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "metadata": METADATA_SCHEMA,
        "lyrics_analysis": LYRICS_ANALYSIS_SCHEMA,
        "uncertainty": UNCERTAINTY_SCHEMA,
    },
    "required": [
        "metadata",
        "lyrics_analysis",
        "uncertainty",
    ],
}