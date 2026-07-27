"""
Parse and structurally validate Song Analyzer JSON data.

This module performs:
1. JSON syntax parsing for the first LLM response.
2. Structural validation of the first LLM response.
3. Structural validation of the completed analysis.json object.

It does not evaluate the analytical quality or grounding of the output.
"""

import json
import logging
from typing import Any
from jsonschema import ValidationError, validate
from schema import FINAL_ANALYSIS_SCHEMA, SONG_ANALYSIS_SCHEMA

logger = logging.getLogger(__name__)

#Parse and Validate first LLM Respomse : Response without metadata included (SONG_ANALYSIS_SCHEMA)
def parse_json(raw: str) -> dict[str, Any] | None:
    """
    Parse and validate the first LLM response.

    Returns:
        The validated response as a Python dictionary.

        None if the response is not valid JSON or does not follow
        SONG_ANALYSIS_SCHEMA.
    """
    try:
        parsed = json.loads(raw)

    except json.JSONDecodeError as exc:
        logger.error("LLM response was not valid JSON. Line: %s, column: %s, reason: %s", exc.lineno, exc.colno, exc.msg)
        return None

    except TypeError as exc:
        logger.error("LLM response could not be parsed because it was not a string: %s", exc)
        return None

    logger.info("LLM response parsed successfully.")

    try:
        validate(instance=parsed, schema=SONG_ANALYSIS_SCHEMA)

    except ValidationError as exc:
        validation_path = ".".join(str(path_part) for path_part in exc.absolute_path)

        logger.error(
            "LLM response failed schema validation. "
            "Field: %s, reason: %s",
            validation_path or "<root>",
            exc.message,
        )
        return None

    logger.info("LLM response passed SONG_ANALYSIS_SCHEMA validation.")

    return parsed


def validate_final_analysis(analysis: dict[str, Any]) -> bool:
    """
    Validate the completed analysis.json object.

    The object must contain:
    - deterministic metadata added by Python
    - lyrics_analysis returned by the LLM
    - uncertainty returned by the LLM

    Returns:
        True when the object follows FINAL_ANALYSIS_SCHEMA.
        False when validation fails.
    """
    try:
        validate(instance=analysis, schema=FINAL_ANALYSIS_SCHEMA)

    except ValidationError as exc:
        validation_path = ".".join(str(path_part) for path_part in exc.absolute_path)

        logger.error(
            "Final analysis failed schema validation. "
            "Field: %s, reason: %s",
            validation_path or "<root>",
            exc.message,
        )
        return False

    logger.info("Final analysis passed FINAL_ANALYSIS_SCHEMA validation.")

    return True