import json
import os
import logging
from openai import OpenAI

from prompts import build_prompt
from models import SONG_ANALYSIS_SCHEMA

logger = logging.getLogger(__name__)


def analyze_lyrics(clean_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "error": "missing_api_key",
            "details": "OPENAI_API_KEY was not found in environment variables."
        }

    client = OpenAI(api_key=api_key)
    prompt = build_prompt(clean_text)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "song_analysis",
                    "strict": True,
                    "schema": SONG_ANALYSIS_SCHEMA
                }
            }
        )

        raw_output = response.output_text

        try:
            parsed = json.loads(raw_output)
            return parsed
        except json.JSONDecodeError:
            logger.error({
                "error": "invalid_json",
                "raw_output": raw_output
            })
            return None

    except Exception as e:
        logger.error({
            "error": "api_failure",
            "details": str(e)
        })
        return None
