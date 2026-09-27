"""Small Google Gemini REST client used by the EduGenie feature modules."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Iterable

import httpx


class GeminiError(RuntimeError):
    """Raised when Gemini cannot produce a response."""


DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_FALLBACK_MODELS = ("gemini-3.5-flash", "gemini-2.5-flash")
MAX_RETRIES_PER_MODEL = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _configured_models() -> list[str]:
    """Return the primary model followed by unique, safe fallback models."""

    primary = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    configured_fallbacks = os.getenv("GEMINI_FALLBACK_MODELS", "")
    fallback_models: Iterable[str] = (
        configured_fallbacks.split(",")
        if configured_fallbacks.strip()
        else DEFAULT_FALLBACK_MODELS
    )

    models: list[str] = []
    for model in [primary, *fallback_models]:
        cleaned = model.strip()
        if cleaned and cleaned not in models:
            models.append(cleaned)
    return models


def _parse_error(response: httpx.Response) -> tuple[str, str]:
    """Extract a safe status and message from a Gemini error response."""

    try:
        body = response.json()
    except ValueError:
        body = {}

    error = body.get("error", {}) if isinstance(body, dict) else {}
    message = error.get("message") if isinstance(error, dict) else None
    status = error.get("status") if isinstance(error, dict) else None
    return (
        str(status or ""),
        str(message or f"Gemini returned HTTP {response.status_code}."),
    )


def _is_quota_error(status_code: int, status: str, message: str) -> bool:
    """Identify errors where retrying the same model would waste quota."""

    lowered_message = message.lower()
    return (
        status == "RESOURCE_EXHAUSTED"
        or "quota" in lowered_message
        or "exceeded your current limit" in lowered_message
        or "rate limit" in lowered_message
        or (status_code == 429 and "capacity" not in lowered_message)
    )


def _retry_delay(attempt: int) -> float:
    """Use a short bounded delay so an interactive request cannot hang."""

    return min(1.5 * (attempt + 1), 5.0)


async def _generate_for_model(
    client: httpx.AsyncClient,
    model: str,
    payload: dict[str, object],
) -> tuple[str | None, GeminiError | None, bool]:
    """Call one model and return (text, error, should_try_another_model)."""

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    last_error: GeminiError | None = None

    for attempt in range(MAX_RETRIES_PER_MODEL):
        try:
            response = await client.post(
                endpoint,
                params={"key": os.environ["GEMINI_API_KEY"]},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError, TypeError, AttributeError) as error:
                raise GeminiError(
                    f"Gemini model {model} returned an empty or unexpected response."
                ) from error
            if not text:
                raise GeminiError(f"Gemini model {model} returned an empty response.")
            return text, None, False
        except httpx.HTTPStatusError as error:
            status, message = _parse_error(error.response)
            last_error = GeminiError(message)
            quota_error = _is_quota_error(error.response.status_code, status, message)

            if quota_error:
                return None, last_error, True
            if (
                error.response.status_code not in RETRYABLE_STATUS_CODES
                or attempt == MAX_RETRIES_PER_MODEL - 1
            ):
                return (
                    None,
                    last_error,
                    error.response.status_code in RETRYABLE_STATUS_CODES
                    or error.response.status_code == 404,
                )
            await asyncio.sleep(_retry_delay(attempt))
        except httpx.HTTPError as error:
            last_error = GeminiError(f"Could not connect to Gemini: {error}")
            if attempt == MAX_RETRIES_PER_MODEL - 1:
                return None, last_error, True
            await asyncio.sleep(_retry_delay(attempt))
        except GeminiError as error:
            return None, error, False

    return None, last_error or GeminiError("Gemini did not return a response."), True


async def generate_with_gemini(prompt: str) -> str:
    """Send one text prompt to Gemini using the environment-provided API key."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError(
            "GEMINI_API_KEY is not configured. Add it to the project secrets "
            "before using EduGenie."
        )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1200,
        },
    }

    errors: list[str] = []
    async with httpx.AsyncClient(timeout=45.0) as client:
        for model in _configured_models():
            text, error, try_another_model = await _generate_for_model(
                client, model, payload
            )
            if text is not None:
                return text
            if error is not None:
                errors.append(f"{model}: {error}")
            if not try_another_model:
                break

    if errors and all("quota" in error.lower() or "limit" in error.lower() for error in errors):
        raise GeminiError(
            "Gemini quota is currently exhausted for the configured models. "
            "Please wait for the quota window to reset or increase the Gemini API "
            "rate limit/billing tier."
        )
    raise GeminiError(errors[-1] if errors else "Gemini did not return a response.")