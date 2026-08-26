import logging
import os

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from song_analyzer.config import LLM_MODEL
from song_analyzer.llm.prompts import build_prompt
from song_analyzer.llm.result import LLMResult
from song_analyzer.reliability.failures import Failure, FailureCode
from song_analyzer.schemas.analysis import SONG_ANALYSIS_SCHEMA


logger = logging.getLogger(__name__)


def analyze_lyrics(
    artist: str,
    song_title: str,
    clean_text: str,
) -> LLMResult:
    """Send one lyrics-analysis request to the LLM."""

    logger.info("Submitting song analysis request for '%s' by '%s'.",song_title,artist)

    api_key = os.getenv("OPENAI_API_KEY")

    # Missing configuration cannot be solved by another API attempt.
    if not api_key:
        logger.error("OPENAI_API_KEY was not found.")

        return LLMResult(
            failure=Failure(
                code=FailureCode.MISSING_API_KEY,
                message="OPENAI_API_KEY was not found.",
            )
        )

    # Retry decisions belong to our application, not the SDK.
    client = OpenAI(
        api_key=api_key,
        max_retries=0,
    )

    prompt = build_prompt(
        artist=artist,
        song_title=song_title,
        clean_text=clean_text,
    )

    try:
        response = client.responses.create(
            model=LLM_MODEL,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "song_analysis",
                    "strict": True,
                    "schema": SONG_ANALYSIS_SCHEMA,
                }
            },
        )

        raw_output = response.output_text

        # The request succeeded technically but produced no usable text.
        if not raw_output:
            logger.error(
                "LLM returned an empty response for '%s' by '%s'.",
                song_title,
                artist,
            )

            return LLMResult(
                failure=Failure(
                    code=FailureCode.LLM_EMPTY_RESPONSE,
                    message="The LLM returned an empty response.",
                )
            )

        logger.info(
            "LLM analysis completed for '%s' by '%s'.",
            song_title,
            artist,
        )

        return LLMResult(output=raw_output)
        
    #------------------------------- OpenAI error types -------------------------------
    # Rate limiting has its own failure classification.
    except RateLimitError as exc:
        logger.exception("LLM request was rate limited.")

        return LLMResult(
            failure=Failure(
                code=FailureCode.API_RATE_LIMITED,
                message="The LLM request was rate limited.",
                details=(str(exc),),
            )
        )

    # Network and timeout problems are temporary infrastructure failures.
    except APIConnectionError as exc:
        logger.exception("Could not connect to the LLM API.")

        return LLMResult(
            failure=Failure(
                code=FailureCode.API_TRANSIENT_ERROR,
                message="Could not connect to the LLM API.",
                details=(str(exc),),
            )
        )

    # Some HTTP failures may be temporary; others indicate a bad request.
    except APIStatusError as exc:
        is_transient = exc.status_code in {408, 409} or exc.status_code >= 500

        failure_code = (
            FailureCode.API_TRANSIENT_ERROR
            if is_transient
            else FailureCode.API_REQUEST_ERROR
        )

        logger.exception(
            "LLM API request failed with status %s.",
            exc.status_code,
        )

        return LLMResult(
            failure=Failure(
                code=failure_code,
                message=f"LLM API request failed with status {exc.status_code}.",
                details=(str(exc),),
            )
        )

    # Unexpected client-side errors are preserved instead of becoming None.
    except Exception as exc:
        logger.exception("Unexpected LLM request failure.")

        return LLMResult(
            failure=Failure(
                code=FailureCode.API_REQUEST_ERROR,
                message="Unexpected LLM request failure.",
                details=(str(exc),),
            )
        )