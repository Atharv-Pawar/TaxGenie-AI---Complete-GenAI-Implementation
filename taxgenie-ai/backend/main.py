"""
TaxGenie AI - FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config import settings
from api.health import router as health_router
from api.upload import router as upload_router
from api.analyze import router as analyze_router
from api.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    logger.info("🧞 TaxGenie AI starting up...")

    # Seed knowledge base if empty
    try:
        from rag.knowledge_base import get_collection_stats
        stats = get_collection_stats()
        if stats.get("available") and stats.get("count", 0) == 0:
            logger.info("Knowledge base empty — running initial seed...")
            from scripts.seed_knowledge_base import seed_knowledge_base
            await seed_knowledge_base()
    except Exception as e:
        logger.warning(f"Auto-seed skipped: {e}")

    logger.info("✅ TaxGenie AI ready!")
    yield
    logger.info("TaxGenie AI shutting down...")


app = FastAPI(
    title="TaxGenie AI",
    description="AI-Native Tax Planning for Every Indian | ET AI Hackathon 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(health_router, tags=["Health"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(analyze_router, prefix="/api/v1", tags=["Analysis"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "TaxGenie AI",
        "tagline": "Your Personal Tax Wizard 🧞",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
