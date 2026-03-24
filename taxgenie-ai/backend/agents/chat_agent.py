"""
TaxGenie AI - Chat Agent
Context-aware conversational agent for tax Q&A.
"""

import logging
from services.llm_gateway import chat_completion
from services.memory_store import get_session, get_chat_history, append_chat_message
from models.response_models import ChatResponse
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are TaxGenie, a friendly and expert Indian tax assistant. You help salaried employees
understand their taxes, deductions, and financial planning.

Your personality:
- Warm and encouraging, like a knowledgeable friend
- Use simple language, avoid jargon
- Always give specific numbers when available from the user's data
- If you don't know something, say so honestly
- Keep responses concise (3-5 sentences max unless they ask for detail)
- Always end with one actionable next step

You have access to this user's tax analysis (provided in context). Use their specific numbers
to personalise every response.

Topics you excel at:
- Old vs New tax regime comparisons
- Section 80C, 80D, HRA, NPS deductions
- Form 16 and ITR filing
- Tax-saving investments (ELSS, PPF, NPS)
- Understanding salary slips and TDS
"""


async def chat_agent(
    session_id: str,
    user_message: str,
) -> ChatResponse:
    """Process a chat message with full context awareness."""
    # Load user's tax data for context
    session = get_session(session_id)
    context = _build_context(session)

    # Load conversation history
    history = get_chat_history(session_id)
    history.append({"role": "user", "content": user_message})

    model = settings.CHAT_MODEL if settings.ANTHROPIC_API_KEY else (
        settings.PDF_PARSER_MODEL if settings.OPENAI_API_KEY else None
    )

    if not model:
        reply = _simple_fallback(user_message)
        append_chat_message(session_id, "user", user_message)
        append_chat_message(session_id, "assistant", reply)
        return ChatResponse(
            response=reply,
            follow_up_suggestions=_suggest_followups(user_message),
        )

    system = SYSTEM_PROMPT + f"\n\nUser's Tax Data:\n{context}"

    try:
        response_text = await chat_completion(
            model=model,
            system_prompt=system,
            messages=history[-10:],  # Keep last 10 turns
            temperature=0.4,
            max_tokens=600,
        )

        append_chat_message(session_id, "user", user_message)
        append_chat_message(session_id, "assistant", response_text)

        return ChatResponse(
            response=response_text,
            sources=_extract_sources(user_message),
            follow_up_suggestions=_suggest_followups(user_message),
        )

    except Exception as e:
        logger.error(f"Chat Agent failed: {e}")
        reply = _simple_fallback(user_message)
        return ChatResponse(
            response=reply,
            follow_up_suggestions=_suggest_followups(user_message),
        )


def _build_context(session: dict | None) -> str:
    if not session:
        return "No tax analysis available yet. Ask the user to upload their Form 16 first."

    lines = []
    if pd := session.get("parsed_data"):
        lines.append(f"Gross Salary: ₹{pd.get('gross_salary', 0):,.0f}")
        lines.append(f"Employer: {pd.get('employer_name', 'Unknown')}")
        lines.append(f"TDS Paid: ₹{pd.get('total_tds_deducted', 0):,.0f}")

    if rc := session.get("regime_comparison"):
        old = rc.get("old_regime", {})
        new = rc.get("new_regime", {})
        lines.append(f"Old Regime Tax: ₹{old.get('total_tax', 0):,.0f}")
        lines.append(f"New Regime Tax: ₹{new.get('total_tax', 0):,.0f}")
        lines.append(f"Recommended: {rc.get('recommended_regime', 'Unknown')} Regime")

    if md := session.get("missed_deductions"):
        missed = md.get("missed_deductions", [])
        lines.append(f"Missed Deductions: {len(missed)} opportunities worth ₹{md.get('total_potential_savings', 0):,.0f}")

    return "\n".join(lines) if lines else "Analysis in progress."


def _extract_sources(message: str) -> list[str]:
    """Return relevant legal sources based on the question."""
    sources = []
    msg = message.lower()
    if "hra" in msg: sources.append("Section 10(13A) - HRA Exemption")
    if "80c" in msg or "elss" in msg or "ppf" in msg: sources.append("Section 80C - Deductions")
    if "80d" in msg or "health" in msg: sources.append("Section 80D - Health Insurance")
    if "nps" in msg: sources.append("Section 80CCD(1B) - NPS")
    if "regime" in msg: sources.append("Finance Act 2023 - New Tax Regime")
    if "87a" in msg: sources.append("Section 87A - Tax Rebate")
    return sources[:3]


def _suggest_followups(message: str) -> list[str]:
    msg = message.lower()
    if "regime" in msg:
        return ["How much can I save with Old Regime if I invest more?",
                "What deductions are available only in Old Regime?"]
    if "80c" in msg or "invest" in msg:
        return ["Which ELSS fund has the best returns?",
                "Should I invest in PPF or ELSS?",
                "What is the maximum I can invest in 80C?"]
    if "hra" in msg:
        return ["What documents do I need for HRA?",
                "Can I claim HRA if I live with parents?"]
    return [
        "Which tax regime is better for me?",
        "What investments can reduce my tax?",
        "How do I claim HRA exemption?",
    ]


def _simple_fallback(message: str) -> str:
    msg = message.lower()
    if "regime" in msg:
        return ("The choice between Old and New Regime depends on your deductions. "
                "Old Regime is better if you have deductions above ~₹3.75L. "
                "Upload your Form 16 and I'll calculate the exact numbers for you!")
    if "hra" in msg:
        return ("HRA exemption = minimum of (actual HRA received, 50% of basic in metro/40% elsewhere, "
                "rent paid minus 10% of basic salary). You'll need rent receipts to claim it.")
    if "80c" in msg:
        return ("Section 80C allows deductions up to ₹1,50,000 per year. "
                "Popular instruments: ELSS (equity, 3yr lock-in), PPF (safe, 15yr), "
                "LIC premium, PF contribution, and NSC.")
    return ("That's a great tax question! For a personalised answer based on your specific income and deductions, "
            "please upload your Form 16 and I'll give you exact numbers.")
