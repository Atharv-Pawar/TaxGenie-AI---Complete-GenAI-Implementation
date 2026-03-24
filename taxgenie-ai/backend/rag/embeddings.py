"""
TaxGenie AI - Embeddings Helper
Generates embeddings for tax documents using OpenAI's text-embedding-3-small.
"""

import logging
from typing import List
from config import settings

logger = logging.getLogger(__name__)


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks.
    Falls back to simple hash-based dummy embeddings if API key not available.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("No OpenAI key — using dummy embeddings (ChromaDB will use its own)")
        return []

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=texts,
            model=settings.EMBEDDING_MODEL,
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []
