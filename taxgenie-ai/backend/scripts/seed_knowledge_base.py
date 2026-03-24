"""
TaxGenie AI - Seed Knowledge Base Script
Loads all tax rule documents into ChromaDB vector store.

Usage:
  python scripts/seed_knowledge_base.py
  python scripts/seed_knowledge_base.py --incremental
"""

import asyncio
import sys
import os
import hashlib
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


TAX_DOCS_DIR = Path(__file__).parent.parent / "rag" / "tax_documents"

CHUNK_SIZE = 800       # characters per chunk
CHUNK_OVERLAP = 150    # overlap between chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at newline
        if end < len(text):
            last_newline = chunk.rfind("\n")
            if last_newline > chunk_size // 2:
                chunk = chunk[:last_newline]
                end = start + last_newline
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 50]


def make_chunk_id(filename: str, index: int, text: str) -> str:
    """Generate a stable ID for a chunk."""
    h = hashlib.md5(text.encode()).hexdigest()[:8]
    return f"{filename}__chunk{index}__{h}"


async def seed_knowledge_base(incremental: bool = False):
    """Load all tax documents into ChromaDB."""
    from rag.knowledge_base import get_collection, get_collection_stats, add_documents

    print("\n🌱 Seeding TaxGenie Knowledge Base...")
    print(f"   Documents directory: {TAX_DOCS_DIR}")

    if not TAX_DOCS_DIR.exists():
        print(f"❌ Tax documents directory not found: {TAX_DOCS_DIR}")
        return

    collection = get_collection()
    if collection is None:
        print("❌ ChromaDB not available. Skipping seed.")
        return

    if incremental:
        stats = get_collection_stats()
        print(f"   Existing chunks: {stats.get('count', 0)} (incremental mode)")

    txt_files = sorted(TAX_DOCS_DIR.glob("*.txt"))
    if not txt_files:
        print("❌ No .txt files found in tax_documents/")
        return

    total_chunks = 0

    for doc_path in txt_files:
        filename = doc_path.stem
        text = doc_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        ids = [make_chunk_id(filename, i, chunk) for i, chunk in enumerate(chunks)]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        if incremental:
            # Skip if IDs already exist
            try:
                existing = collection.get(ids=ids)
                existing_ids = set(existing.get("ids", []))
                new_chunks = [(c, i, m) for c, i, m in zip(chunks, ids, metadatas) if i not in existing_ids]
                if not new_chunks:
                    print(f"   ⏭  {doc_path.name} — already loaded, skipping")
                    continue
                chunks, ids, metadatas = zip(*new_chunks)
                chunks, ids, metadatas = list(chunks), list(ids), list(metadatas)
            except Exception:
                pass

        success = add_documents(chunks, ids, metadatas)
        status = "✅" if success else "❌"
        print(f"   {status} {doc_path.name:<40} {len(chunks)} chunks loaded")
        if success:
            total_chunks += len(chunks)

    print(f"\n✅ Knowledge base seeded successfully!")
    print(f"📊 Total chunks added: {total_chunks}")
    print(f"🔍 Vector store ready for queries\n")


if __name__ == "__main__":
    incremental = "--incremental" in sys.argv
    asyncio.run(seed_knowledge_base(incremental=incremental))
