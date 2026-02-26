"""
Q&A endpoint — backed by NOVYRA Reasoning Engine (no LangChain)

Legacy path kept at /api/qa so the frontend proxy continues to work.
Internally delegates to reasoning_service which calls Gemini directly.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.services import reasoning_service

logger = logging.getLogger(__name__)
router = APIRouter()


class QAInput(BaseModel):
    question: str = Field(..., description="User question")
    userId: Optional[str] = None
    language: Optional[str] = "en"
    collection_name: Optional[str] = "default"
    conversation_history: Optional[List[Dict[str, Any]]] = None
    system_prompt: Optional[str] = None


@router.get("/greeting")
async def get_greeting():
    return {"greeting": "Hi! I'm NOVYRA ⚡ — your adaptive AI tutor. Ask me anything!"}


@router.get("/health")
async def qa_health():
    return {"status": "healthy", "backend": "NOVYRA Reasoning Engine (Gemini)"}


@router.post("/", summary="Ask a question (legacy /api/qa)")
async def post_qa(payload: QAInput):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = await reasoning_service.reason(
            question=payload.question.strip(),
            user_id=payload.userId,
            language=payload.language or "en",
            include_hints=True,
        )
        # Return in legacy-compatible shape so frontend doesn't break
        return {
            "answer": result.final_solution,
            "concept": result.concept,
            "prerequisites": result.prerequisites,
            "stepwise_reasoning": result.stepwise_reasoning,
            "hint_ladder": result.hint_ladder,
            "confidence_score": result.confidence_score,
            "related_concepts": result.related_concepts,
            "sources": [],
            "mode": "reasoning_engine",
            "follow_up_questions": result.related_concepts[:3],
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        logger.exception("QA reasoning failed")
        raise HTTPException(status_code=500, detail="Reasoning engine error")

