"""
TaxGenie AI - RAG Knowledge Base
ChromaDB vector store operations for tax rule retrieval.
"""

import logging
import os
from typing import List
from config import settings

logger = logging.getLogger(__name__)

# Try to initialise ChromaDB
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    _chroma_client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIRECTORY,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    CHROMA_AVAILABLE = True
    logger.info("ChromaDB initialised successfully")
except Exception as e:
    logger.warning(f"ChromaDB not available: {e}")
    _chroma_client = None
    CHROMA_AVAILABLE = False

COLLECTION_NAME = "taxgenie_knowledge"


def get_collection():
    """Get or create the tax knowledge collection."""
    if not CHROMA_AVAILABLE:
        return None
    try:
        return _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as e:
        logger.error(f"Failed to get collection: {e}")
        return None


def query_knowledge_base(query: str, n_results: int = 5) -> List[str]:
    """
    Search the tax knowledge base for relevant rules.
    Returns a list of relevant text chunks.
    """
    collection = get_collection()
    if not collection:
        return _fallback_knowledge(query)

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        documents = results.get("documents", [[]])[0]
        return documents if documents else _fallback_knowledge(query)
    except Exception as e:
        logger.error(f"Knowledge base query failed: {e}")
        return _fallback_knowledge(query)


def add_documents(texts: List[str], ids: List[str], metadatas: List[dict] = None) -> bool:
    """Add documents to the knowledge base."""
    collection = get_collection()
    if not collection:
        return False

    try:
        collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas or [{}] * len(texts),
        )
        return True
    except Exception as e:
        logger.error(f"Failed to add documents: {e}")
        return False


def get_collection_stats() -> dict:
    """Return stats about the knowledge base."""
    collection = get_collection()
    if not collection:
        return {"available": False, "count": 0}
    try:
        return {"available": True, "count": collection.count()}
    except Exception:
        return {"available": False, "count": 0}


def _fallback_knowledge(query: str) -> List[str]:
    """Return hardcoded tax rules when ChromaDB is unavailable."""
    q = query.lower()
    chunks = []

    if "80c" in q or "elss" in q or "ppf" in q:
        chunks.append(
            "Section 80C: Deduction up to ₹1,50,000 for investments in PF, PPF, ELSS, "
            "LIC premium, NSC, home loan principal repayment, tuition fees for children. "
            "ELSS has shortest lock-in of 3 years. PPF has 15-year tenure with tax-free returns."
        )
    if "80d" in q or "health" in q:
        chunks.append(
            "Section 80D: Deduction for health insurance premiums. Up to ₹25,000 for self and family. "
            "Up to ₹25,000 additional for parents (₹50,000 if parents are senior citizens). "
            "Preventive health check-up included up to ₹5,000 within the limit."
        )
    if "hra" in q:
        chunks.append(
            "HRA Exemption (Section 10(13A)): Minimum of — (1) actual HRA received, "
            "(2) 50% of basic salary for metro cities (Delhi, Mumbai, Chennai, Kolkata) or 40% elsewhere, "
            "(3) actual rent paid minus 10% of basic salary. "
            "Requires landlord PAN if annual rent > ₹1,00,000."
        )
    if "new regime" in q or "new tax" in q:
        chunks.append(
            "New Tax Regime FY 2024-25: Standard deduction ₹75,000. Tax slabs: 0% up to ₹3L, "
            "5% ₹3-6L, 10% ₹6-9L, 15% ₹9-12L, 20% ₹12-15L, 30% above ₹15L. "
            "Section 87A rebate: up to ₹25,000 if income ≤ ₹7L (making effective tax zero). "
            "Most deductions (80C, 80D, HRA) are NOT available in New Regime."
        )
    if "nps" in q or "80ccd" in q:
        chunks.append(
            "Section 80CCD(1B): Additional deduction of up to ₹50,000 for NPS contributions, "
            "OVER and ABOVE the ₹1,50,000 limit of Section 80C. "
            "Available only in Old Regime. Tier-1 NPS account required."
        )
    if not chunks:
        chunks.append(
            "Indian Income Tax FY 2024-25: Old Regime allows deductions (80C, 80D, HRA, etc.). "
            "New Regime has lower slab rates but fewer deductions. "
            "Standard deduction: ₹50,000 (old) / ₹75,000 (new). "
            "Section 87A rebate makes tax zero for income ≤ ₹5L (old) or ≤ ₹7L (new)."
        )

    return chunks
