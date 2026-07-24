import json
import os
import logging
from openai import OpenAI

from prompts import build_prompt
from schema import SONG_ANALYSIS_SCHEMA
from utils import LLM_Model

logger = logging.getLogger(__name__)


def analyze_lyrics(clean_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "error": "missing_api_key",
            "details": "OPENAI_API_KEY was not found in environment variables."
        }

    client = OpenAI(api_key=api_key) # API client call
    prompt = build_prompt(clean_text) # call the prompt from prompts.py

    try:
        response = client.responses.create(
            model= LLM_Model,
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

        raw_output = response.output_text # the text as string not json yet

            #parsed = json.loads(raw_output) #parsed json to python dictionary
            #return parsed
        return raw_output

    except Exception as e: # error when API fails
        logger.error({
            "error": "api_failure",
            "details": str(e)
        })
        return None
