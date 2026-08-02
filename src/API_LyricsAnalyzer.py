import os
import logging
from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError

from prompts import build_prompt
from schema import SONG_ANALYSIS_SCHEMA
from _utils import LLM_Model

logger = logging.getLogger(__name__)

# Explicit client limits instead of the SDK defaults (600s timeout).
# A stuck connection should fail within minutes, not silently hang the run.
REQUEST_TIMEOUT_S = 120
MAX_RETRIES = 2
MAX_OUTPUT_TOKENS = 4096


def analyze_lyrics( artist: str, song_title: str, clean_text: str) -> str | None:

    logger.info("Submitting song analysis request for '%s' by '%s'", song_title, artist
                )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "OPENAI_API_KEY was not found in the environment variables."
        )
        return None

    client = OpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT_S, max_retries=MAX_RETRIES) # API client call
    prompt = build_prompt(artist=artist, song_title=song_title, clean_text=clean_text) # call the prompt from prompts.py

    try:
        response = client.responses.create(
            model= LLM_Model,
            input=prompt,
            # temperature=0 keeps repeated runs of the same song as stable as the
            # model allows -- a prerequisite for comparing analyses across weeks.
            temperature=0,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "song_analysis",
                    "strict": True,
                    "schema": SONG_ANALYSIS_SCHEMA
                }
            }
        )

    except AuthenticationError as e:
        logger.error("OpenAI rejected the API key (invalid or revoked). Fix OPENAI_API_KEY in .env. Details: %s", e)
        return None

    except RateLimitError as e:
        if getattr(e, "code", None) == "insufficient_quota" or "insufficient_quota" in str(e):
            logger.error("The OpenAI account has no remaining credits (insufficient_quota). Retrying cannot help; add credits first.")
        else:
            logger.error("OpenAI rate limit reached; wait a moment and run again. Details: %s", e)
        return None

    except APIConnectionError as e: # includes timeouts
        logger.error("Could not reach the OpenAI API (network problem or %ss timeout): %s", REQUEST_TIMEOUT_S, e)
        return None

    except Exception: # any other API failure
        logger.exception("LLM request failed for '%s' by '%s'",  song_title, artist)
        return None

    # A truncated response (token limit, content filter) must not reach the JSON
    # parser -- it would surface later as a misleading "not valid JSON" error.
    if getattr(response, "status", None) == "incomplete":
        reason = getattr(getattr(response, "incomplete_details", None), "reason", "unknown")
        logger.error("The LLM response is incomplete (reason: %s). Discarding it.", reason)
        return None

    raw_output = response.output_text # the text as string not json yet

    if not raw_output:
        logger.error("The LLM returned an empty text output (possibly a refusal). Discarding it.")
        return None

    logger.info( "LLM analysis completed for '%s' by '%s'", song_title, artist)

    return raw_output
