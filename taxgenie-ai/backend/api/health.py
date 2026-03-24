"""
TaxGenie AI - Health Check API
"""

from fastapi import APIRouter
from models.response_models import HealthResponse
from services.memory_store import health_check as memory_health
from rag.knowledge_base import get_collection_stats

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    mem = memory_health()
    kb = get_collection_stats()

    return HealthResponse(
        status="ok",
        version="1.0.0",
        services={
            "redis": "connected" if mem.get("redis_available") else "fallback (in-memory)",
            "chromadb": f"connected ({kb.get('count', 0)} chunks)" if kb.get("available") else "not available",
        },
    )
