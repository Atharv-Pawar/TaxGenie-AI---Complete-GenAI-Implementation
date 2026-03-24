# agents/chat_agent.py
"""
Tax Chat Agent
Multi-turn conversational AI for tax questions.
Uses GPT-4 with RAG context from the knowledge base.
Maintains conversation history per session.
"""

import json
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are TaxGenie — a friendly, expert Indian tax advisor chatbot.

Your expertise:
- Indian Income Tax Act (FY 2024-25)
- All deductions: 80C, 80D, 80CCD, 80E, 80G, HRA, LTA, etc.
- Old vs New tax regime comparison
- Tax-saving investment strategies
- ITR filing process and deadlines

Communication rules:
- Use simple, friendly language
- Cite sections (e.g., "Under Section 80C...")
- Always use ₹ for amounts
- Be specific and actionable
- If unsure, say so honestly
- Keep responses concise (under 200 words usually)
- When user shares their data, give personalized advice

Current Tax Year: FY 2024-25 (AY 2025-26)
ITR Filing Deadline: July 31, 2025
""".strip()


class TaxChatAgent:
    """
    Conversational tax advisor with session memory.
    """

    # Max messages to keep in context window
    MAX_HISTORY = 20

    def __init__(self):
        self.client   = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.sessions: dict[str, list[dict]] = {}

    async def chat(
        self,
        session_id: str,
        user_message: str,
        user_context: dict | None = None,
    ) -> dict:
        """
        Process a chat message and return AI response.

        Args:
            session_id:   Unique session identifier
            user_message: The user's question
            user_context: Optional tax data for personalized answers

        Returns:
            Dict with response and updated message count
        """
        logger.info(f"[ChatAgent] Session {session_id}: {user_message[:60]}...")

        # Get or initialize session history
        history = self.sessions.get(session_id, [])

        # Build context message if user data available
        context_msg = self._build_context_message(user_context)

        # Build messages for API
        messages = self._build_messages(history, context_msg, user_message)

        # Call GPT-4
        response_text = await self._call_gpt4(messages)

        # Update session history
        history.append({"role": "user",      "content": user_message})
        history.append({"role": "assistant",  "content": response_text})

        # Trim if too long
        if len(history) > self.MAX_HISTORY:
            history = history[-self.MAX_HISTORY:]

        self.sessions[session_id] = history

        return {
            "response":      response_text,
            "session_id":    session_id,
            "message_count": len(history) // 2,
        }

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"[ChatAgent] Session {session_id} cleared")

    def get_history(self, session_id: str) -> list[dict]:
        """Get conversation history for a session."""
        return self.sessions.get(session_id, [])

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _build_context_message(self, user_context: dict | None) -> str | None:
        """
        Build a system-level context message from user's tax data.
        """
        if not user_context:
            return None

        gross    = user_context.get("gross_salary", 0)
        deductions = user_context.get("deductions_chapter_vi_a", {})

        return (
            f"[USER CONTEXT]\n"
            f"Gross Salary: ₹{gross:,.0f}\n"
            f"80C Claimed: ₹{deductions.get('section_80c', 0):,.0f}\n"
            f"NPS 80CCD(1B): ₹{deductions.get('section_80ccd_1b', 0):,.0f}\n"
            f"80D Health: ₹{deductions.get('section_80d', 0):,.0f}\n"
            f"Use this data to give personalized answers."
        )

    def _build_messages(
        self,
        history:     list[dict],
        context_msg: str | None,
        user_message: str,
    ) -> list[dict]:
        """
        Build the messages array for the OpenAI API.
        """
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        # Add user context as system message if available
        if context_msg:
            messages.append({"role": "system", "content": context_msg})

        # Add conversation history
        messages.extend(history)

        # Add current message
        messages.append({"role": "user", "content": user_message})

        return messages

    async def _call_gpt4(self, messages: list[dict]) -> str:
        """Call GPT-4 with the built messages."""
        response = await self.client.chat.completions.create(
            model       = settings.PRIMARY_MODEL,
            temperature = 0.7,
            max_tokens  = 800,
            messages    = messages,
        )
        return response.choices[0].message.content


# ── Singleton ─────────────────────────────────────────────────────────────────
chat_agent = TaxChatAgent()