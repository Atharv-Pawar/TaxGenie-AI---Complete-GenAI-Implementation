"""
TaxGenie AI - Analysis API
Runs the full LangGraph pipeline and streams progress via WebSocket.
"""

import uuid
import base64
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional

from orchestrator.graph import taxgenie_graph
from orchestrator.state import TaxGenieState
from services.memory_store import get_session, save_session
from models.response_models import RiskProfile, AnalysisResult

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory WebSocket connection registry
_ws_connections: dict[str, WebSocket] = {}


async def _send_progress(session_id: str, stage: str, message: str, progress: int):
    """Send progress update to connected WebSocket client."""
    ws = _ws_connections.get(session_id)
    if ws:
        try:
            import json
            await ws.send_text(json.dumps({
                "stage": stage,
                "message": message,
                "progress": progress,
            }))
        except Exception:
            pass


@router.post("/analyze")
async def analyze(
    session_id: str = Form(...),
    risk_profile: str = Form("moderate"),
    additional_rent_paid: Optional[float] = Form(None),
    manual_income: Optional[float] = Form(None),
):
    """
    Trigger full tax analysis for an uploaded PDF.
    Runs the LangGraph pipeline asynchronously.
    Returns immediately; poll GET /results/{session_id} or use WebSocket for progress.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a PDF first.")

    # Mark as processing
    save_session(session_id, {**session, "status": "processing"})

    # Run analysis in background
    asyncio.create_task(_run_analysis(
        session_id=session_id,
        session=session,
        risk_profile=risk_profile,
        manual_income=manual_income,
        additional_rent_paid=additional_rent_paid,
    ))

    return {
        "session_id": session_id,
        "status": "processing",
        "estimated_time_seconds": 45,
        "websocket_url": f"/ws/session/{session_id}",
        "poll_url": f"/api/v1/results/{session_id}",
    }


@router.post("/analyze/sync")
async def analyze_sync(
    session_id: str = Form(...),
    risk_profile: str = Form("moderate"),
    additional_rent_paid: Optional[float] = Form(None),
    manual_income: Optional[float] = Form(None),
):
    """
    Synchronous version of analyze — waits for full result.
    Useful for testing and simple clients.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    result = await _run_analysis(
        session_id=session_id,
        session=session,
        risk_profile=risk_profile,
        manual_income=manual_income,
        additional_rent_paid=additional_rent_paid,
    )
    return result


async def _run_analysis(
    session_id: str,
    session: dict,
    risk_profile: str,
    manual_income: Optional[float],
    additional_rent_paid: Optional[float],
) -> dict:
    """Execute the LangGraph pipeline."""
    try:
        await _send_progress(session_id, "parsing", "🔄 Parsing your Form 16...", 10)

        # Decode PDF bytes from session
        pdf_b64 = session.get("pdf_b64")
        pdf_bytes = base64.b64decode(pdf_b64) if pdf_b64 else None

        # Build initial state
        initial_state: TaxGenieState = {
            "session_id": session_id,
            "pdf_bytes": pdf_bytes,
            "manual_income": manual_income,
            "risk_profile": RiskProfile(risk_profile),
            "additional_rent_paid": additional_rent_paid,
            "parsed_data": None,
            "missed_deductions": None,
            "regime_comparison": None,
            "investment_recommendations": [],
            "summary": None,
            "current_stage": "start",
            "progress": 0,
            "error": None,
            "total_potential_savings": 0,
        }

        await _send_progress(session_id, "analyzing", "🔍 Finding missed deductions...", 30)

        # Run the graph
        final_state = await taxgenie_graph.ainvoke(initial_state)

        await _send_progress(session_id, "calculating", "⚖️ Comparing tax regimes...", 65)
        await asyncio.sleep(0.1)
        await _send_progress(session_id, "recommending", "📈 Building investment plan...", 85)
        await asyncio.sleep(0.1)
        await _send_progress(session_id, "done", "✅ Report ready!", 100)

        # Return stored result
        return get_session(session_id) or {"status": "completed", "error": "Result not stored"}

    except Exception as e:
        logger.error(f"Analysis failed for session {session_id}: {e}")
        error_data = {"status": "failed", "error": str(e)}
        save_session(session_id, error_data)
        await _send_progress(session_id, "error", f"❌ Analysis failed: {str(e)}", 0)
        return error_data


@router.get("/results/{session_id}")
async def get_results(session_id: str):
    """
    Poll for analysis results. Returns current state of the analysis.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return session


@router.websocket("/ws/session/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    Connect before calling POST /analyze for live updates.
    """
    await websocket.accept()
    _ws_connections[session_id] = websocket
    logger.info(f"WebSocket connected for session {session_id}")

    try:
        # Keep alive until client disconnects
        while True:
            data = await websocket.receive_text()
            # Echo back any client messages (heartbeat)
            await websocket.send_text(data)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    finally:
        _ws_connections.pop(session_id, None)
