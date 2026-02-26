"""
NOVYRA — Structured Reasoning Engine

No LangChain. Pure Gemini SDK + Pydantic validation.

Flow:
  1. Detect language of question
  2. If non-English → translate to English
  3. Fetch graph context for enriched prompt
  4. Call Gemini with REASONING_PROMPT → enforce JSON schema
  5. Validate with Pydantic
  6. If non-English → translate final_solution back
  7. Return ReasoningResponse
"""
from __future__ import annotations
import json
import logging
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.llm import generate_json
from app.core.prompts import REASONING_SYSTEM, REASONING_PROMPT
from app.schemas.reasoning import ReasoningResponse
from app.services import multilingual_service as ml
from app.services import knowledge_graph_service as kg

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=8))
async def reason(
    question: str,
    user_id: Optional[str] = None,
    language: str = "en",
    include_hints: bool = True,
) -> ReasoningResponse:
    """
    Core reasoning entry-point.
    Returns a validated ReasoningResponse.
    """
    # --- 1. Translate to English if needed ---
    working_question = question
    if language != "en":
        working_question = await ml.to_english(question, source_lang=language)
        logger.info("Translated question: %s → %s", question[:60], working_question[:60])

    # --- 2. Fetch graph context ---
    graph_context = "No graph context available."
    if user_id:
        try:
            # Try to extract concept name from question (simple heuristic: first noun phrase)
            # A richer approach would use a dedicated concept-extraction call
            concept_guess = working_question.split("?")[0][:80]
            ctx = await kg.fetch_concept_context(concept_guess)
            if ctx["prerequisites"] or ctx["related"]:
                graph_context = (
                    f"Prerequisites: {', '.join(ctx['prerequisites']) or 'none'}. "
                    f"Related concepts: {', '.join(ctx['related']) or 'none'}."
                )
        except Exception as exc:
            logger.warning("Graph context fetch failed: %s", exc)

    # --- 3. Build prompt ---
    prompt = REASONING_PROMPT.format(
        question=working_question,
        graph_context=graph_context,
    )

    # --- 4. Call LLM ---
    raw: dict = await generate_json(prompt, system_prompt=REASONING_SYSTEM)

    # --- 5. Validate ---
    # Strip hint_ladder if caller doesn't want it
    if not include_hints:
        raw["hint_ladder"] = []

    response = ReasoningResponse(**raw)

    # --- 6. Translate answer back ---
    if language != "en":
        response.final_solution = await ml.from_english(
            response.final_solution, target_lang=language
        )
        response.language = language

    return response
