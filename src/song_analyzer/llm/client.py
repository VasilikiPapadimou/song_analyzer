import os
import logging
from openai import OpenAI

from song_analyzer.llm.prompts import build_prompt
from song_analyzer.schemas.analysis import SONG_ANALYSIS_SCHEMA
from song_analyzer.config import LLM_MODEL
logger = logging.getLogger(__name__)


def analyze_lyrics( artist: str, song_title: str, clean_text: str) -> str | None:

    logger.info("Submitting song analysis request for '%s' by '%s'", song_title, artist
                )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "OPENAI_API_KEY was not found in the environment variables."
        )
        return None

    client = OpenAI(api_key=api_key) # API client call
    prompt = build_prompt(artist=artist, song_title=song_title, clean_text=clean_text) # call the prompt from prompts.py

    try:
        response = client.responses.create(
            model= LLM_MODEL,
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
        logger.info( "LLM analysis completed for '%s' by '%s'", song_title, artist)

        return raw_output

    except Exception as e: # error when API fails
        logger.error({
            "error": "api_failure",
            "details": str(e)
        })
        logger.exception("LLM request failed for '%s' by '%s'",  song_title, artist)
        return None
