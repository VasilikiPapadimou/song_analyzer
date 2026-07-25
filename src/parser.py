"""
This module gets the raw output from LLM and parses it.
After parsing the product is a python dictionary
Syntax Validation : parse_json() checks if the json produced has the correct syntax (brackets/commas)
"""

"""
MISSING :
    Are all required fields present?
    Are the fields in the right type?
    Does the JSON structure match your schema contract?
"""
import json
import logging
from schema import SONG_ANALYSIS_SCHEMA
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


def parse_json(raw: str):
    """
    Step 1: Parse raw JSON string → Python dict
    Step 2: Validate dict against schema
    """

    # ------------------------
    # STEP 1 — Syntax parsing
    # ------------------------
    try:
        parsed = json.loads(raw)
        logger.info("LLM response parsed successfully.")
    except json.JSONDecodeError :
        logger.exception("LLM response was not valid JSON.")

        return None

    # ------------------------
    # STEP 2 — Schema validation
    # ------------------------
    try:
        validate(instance=parsed, schema=SONG_ANALYSIS_SCHEMA)
    except ValidationError:
        logger.exception("LLM response failed schema validation.")
        return None

    # ------------------------
    # SUCCESS
    # ------------------------
    logger.info("Parsed response passed schema validation.")
    return parsed
