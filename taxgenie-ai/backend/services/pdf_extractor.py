"""
TaxGenie AI - PDF Extractor Service
Extracts raw text from uploaded PDFs using PyMuPDF.
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF while preserving layout as much as possible.
    Returns the full text as a single string.
    """
    try:
        doc = fitz.open(file_path)
        all_text = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            all_text.append(f"--- Page {page_num + 1} ---\n{text}")

        doc.close()
        return "\n\n".join(all_text)

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Could not read PDF file: {str(e)}")


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF given raw bytes."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        all_text = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            all_text.append(f"--- Page {page_num + 1} ---\n{text}")

        doc.close()
        return "\n\n".join(all_text)

    except Exception as e:
        logger.error(f"PDF bytes extraction failed: {e}")
        raise ValueError(f"Could not parse PDF: {str(e)}")


def get_pdf_metadata(file_path: str) -> dict:
    """Return basic metadata about the PDF."""
    try:
        doc = fitz.open(file_path)
        meta = {
            "page_count": doc.page_count,
            "metadata": doc.metadata,
        }
        doc.close()
        return meta
    except Exception as e:
        return {"error": str(e)}
