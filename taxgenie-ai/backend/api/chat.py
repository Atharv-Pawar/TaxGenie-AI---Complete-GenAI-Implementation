"""
TaxGenie AI - Chat API
Context-aware Q&A about the user's specific tax situation.
"""

import logging
from fastapi import APIRouter, HTTPException
from models.response_models import ChatRequest, ChatResponse
from agents.chat_agent import chat_agent
from services.memory_store import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to TaxGenie chatbot.
    Uses the session's tax analysis as context for personalised answers.
    """
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    # Validate session exists (warn but don't fail — can still answer general questions)
    session = get_session(request.session_id)
    if not session:
        logger.warning(f"Chat request for unknown session: {request.session_id}")

    response = await chat_agent(
        session_id=request.session_id,
        user_message=request.message,
    )
    return response


@router.get("/chat/history/{session_id}")
async def get_chat_history_endpoint(session_id: str):
    """Return chat history for a session."""
    from services.memory_store import get_chat_history
    history = get_chat_history(session_id)
    return {"session_id": session_id, "messages": history, "count": len(history)}


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    from services.memory_store import save_chat_history
    save_chat_history(session_id, [])
    return {"message": "Chat history cleared"}
