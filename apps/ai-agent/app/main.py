"""
NOVYRA AI Engine — FastAPI Application

Mounts both legacy routes (qa, documents, quiz, flashcards, mindmap)
and new NOVYRA core engines (reasoning, evaluation, mastery, graph).
Port 8000 — unchanged so the Next.js frontend proxy continues to work.
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
from app.core.config import settings, validate_settings  # noqa: E402

validate_settings()

# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
from app.services.knowledge_graph_service import ping as neo4j_ping, close_driver  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 70)
    logger.info("NOVYRA AI Engine starting on port %s", settings.PORT)
    logger.info("    LLM   : %s", settings.LLM_MODEL)
    logger.info("    Neo4j : %s", settings.NEO4J_URI)
    logger.info("=" * 70)

    neo4j_ok = await neo4j_ping()
    if neo4j_ok:
        logger.info("Neo4j connection OK")
    else:
        logger.warning("Neo4j unreachable — graph features degraded")

    yield  # app runs here

    await close_driver()
    logger.info("NOVYRA AI Engine stopped.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="NOVYRA AI Engine",
    description=(
        "Structured Reasoning · Rubric Evaluation · Mastery Tracking · "
        "Knowledge Graph · Multilingual Layer"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
cors_origins = settings.get_allowed_origins_list()
if "*" in cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Route registry helper
# ---------------------------------------------------------------------------
api_router = APIRouter()


def _mount(tag: str, module_path: str, prefix: str):
    """Try to import a route module and register it. Logs failures gracefully."""
    try:
        import importlib
        mod = importlib.import_module(module_path)
        api_router.include_router(mod.router, prefix=prefix, tags=[tag])
        logger.info("%-20s -> /api%s", tag, prefix)
    except Exception as exc:
        logger.error("%s route failed to load: %s", tag, exc)


# ---------------------------------------------------------------------------
# NOVYRA Core Engines  (new)
# ---------------------------------------------------------------------------
_mount("reasoning",  "app.api.routes.reasoning",  "/reasoning")
_mount("evaluation", "app.api.routes.evaluation",  "/evaluation")
_mount("mastery",    "app.api.routes.mastery",     "/mastery")
_mount("graph",      "app.api.routes.graph",       "/graph")

# ---------------------------------------------------------------------------
# Legacy / existing routes  (keep working for frontend)
# ---------------------------------------------------------------------------
_mount("qa",         "app.api.routes.qa",          "/qa")
_mount("documents",  "app.api.routes.documents",   "/documents")
_mount("quiz",       "app.api.routes.quiz",        "/quiz")
_mount("flashcards", "app.api.routes.flashcards",  "/flashcards")
_mount("mindmap",    "app.api.routes.mindmap",     "/mindmap")

app.include_router(api_router, prefix="/api")


# ---------------------------------------------------------------------------
# Health & root
# ---------------------------------------------------------------------------
@app.get("/health", tags=["ops"])
async def health():
    neo4j_ok = await neo4j_ping()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "llm_model": settings.LLM_MODEL,
        "google_api_key_set": bool(settings.GOOGLE_API_KEY),
        "neo4j_connected": neo4j_ok,
    }


@app.get("/", tags=["ops"])
async def root():
    return {
        "service": "NOVYRA AI Engine",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "engines": {
            "reasoning":  "/api/reasoning/ask",
            "evaluation": "/api/evaluation/evaluate",
            "mastery":    "/api/mastery/attempt",
            "graph":      "/api/graph/concept",
        },
        "legacy": {
            "qa":         "/api/qa",
            "documents":  "/api/documents",
            "quiz":       "/api/quiz",
            "flashcards": "/api/flashcards",
            "mindmap":    "/api/mindmap",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
