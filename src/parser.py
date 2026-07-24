'''
    This module gets the raw output from LLM and parses it. 
    After parsing the product is a python dictionary 
    Syntax Validation : parse_json() checks if the json produced has the correct syntax (brackets/commas)
'''

"""
MISSING :
    Are all required fields present?
    Are the fields in the right type?
    Does the JSON structure match your schema contract?
"""
import json
import logging
from schema import SONG_ANALYSIS_SCHEMA
from jsonschema import validate,ValidationError

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
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        return None
    
    # ------------------------
    # STEP 2 — Schema validation
    # ------------------------
    try: 
        validate(instance=parsed,schema=SONG_ANALYSIS_SCHEMA)
    except ValidationError as e:
        logger.error(f"❌ Schema validation failed: {e.message}")
        return None

    # ------------------------
    # SUCCESS
    # ------------------------
    logger.info("✅ JSON parsed and validated successfully")
    return parsed