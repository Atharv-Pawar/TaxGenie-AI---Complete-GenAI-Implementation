"""
TaxGenie AI - File Upload API
Handles PDF upload and initiates analysis session.
"""

import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.memory_store import save_session
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a Form 16 PDF. Returns a session_id for tracking analysis.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Validate file size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB.",
        )

    # Create session
    session_id = str(uuid.uuid4())

    # Store PDF bytes temporarily in session
    import base64
    save_session(session_id, {
        "status": "uploaded",
        "filename": file.filename,
        "pdf_b64": base64.b64encode(contents).decode("utf-8"),
    })

    logger.info(f"PDF uploaded: {file.filename} | Session: {session_id} | Size: {size_mb:.2f}MB")

    return {
        "session_id": session_id,
        "filename": file.filename,
        "size_mb": round(size_mb, 2),
        "status": "uploaded",
        "message": "File uploaded successfully. Call /analyze to start analysis.",
    }
