"""
NOVYRA — Barebones Gemini LLM client (no LangChain)
"""
import json
import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure SDK once at import time
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    logger.info("Gemini SDK configured with model: %s", settings.LLM_MODEL)
else:
    logger.warning("GOOGLE_API_KEY not set — Gemini calls will fail")


def _get_model(temperature: float | None = None) -> genai.GenerativeModel:
    """Return a configured GenerativeModel instance."""
    gen_config = genai.GenerationConfig(
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_output_tokens=4096,
    )
    return genai.GenerativeModel(
        model_name=settings.LLM_MODEL,
        generation_config=gen_config,
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_text(
    prompt: str,
    system_prompt: str = "You are a helpful AI tutor.",
    temperature: float | None = None,
) -> str:
    """
    Single-turn text generation — returns plain string.
    System prompt is prepended as context since Gemini uses user-only chat turns.
    """
    model = _get_model(temperature)
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = await model.generate_content_async(full_prompt)
    return response.text.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_json(
    prompt: str,
    system_prompt: str = "You are a helpful AI tutor. Respond ONLY with valid JSON.",
    temperature: float | None = None,
) -> dict:
    """
    Generate structured JSON output.
    Retries up to 3 times if output is not valid JSON.
    """
    model = _get_model(temperature)
    full_prompt = (
        f"{system_prompt}\n\n"
        f"CRITICAL: Your entire response must be a single valid JSON object.\n"
        f"Do NOT include markdown code fences, just raw JSON.\n\n"
        f"{prompt}"
    )
    response = await model.generate_content_async(full_prompt)
    text = response.text.strip()

    # Strip code fences if model added them anyway
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse failed: %s | raw: %s", exc, text[:300])
        raise ValueError(f"LLM did not return valid JSON: {exc}") from exc
