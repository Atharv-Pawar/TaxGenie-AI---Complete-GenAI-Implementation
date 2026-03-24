"""
TaxGenie AI - Explainer Agent
Claude 3.5 Sonnet generates plain-English summaries of tax analysis.
"""

import logging
from services.llm_gateway import llm_call
from models.response_models import (
    ParsedFormData, DeductionResult, RegimeComparison, InvestmentRecommendation
)
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are TaxGenie, a friendly Indian tax assistant. Your job is to explain complex tax analysis
in simple, encouraging language that any Indian salaried employee can understand.

Write a personalised summary (150-200 words) that:
1. Opens with the biggest win (e.g., "Great news! You can save ₹XX,XXX in taxes!")
2. Explains the regime recommendation in ONE simple sentence
3. Lists the top 2-3 missed deductions with actionable steps
4. Ends with one clear priority action they should take this week

Tone: Warm, encouraging, and clear. Like a knowledgeable friend, not a government notice.
Use ₹ for currency. Keep it conversational. No jargon.
"""


async def explainer_agent(
    parsed_data: ParsedFormData,
    deductions: DeductionResult,
    regime: RegimeComparison,
    investments: list[InvestmentRecommendation],
) -> str:
    """Generate a plain-English summary of the full tax analysis."""
    if not settings.ANTHROPIC_API_KEY:
        return _template_summary(parsed_data, deductions, regime)

    try:
        user_message = f"""
Taxpayer Summary:
- Salary: ₹{parsed_data.gross_salary:,.0f} at {parsed_data.employer_name or 'their employer'}
- Recommended Regime: {regime.recommended_regime} (saves ₹{regime.savings_with_recommended:,.0f})
- Current Tax: ₹{regime.old_regime.total_tax if regime.recommended_regime == 'NEW' else regime.new_regime.total_tax:,.0f}
- After Optimisation: ₹{regime.new_regime.total_tax if regime.recommended_regime == 'NEW' else regime.old_regime.total_tax:,.0f}
- Total Additional Potential Savings: ₹{deductions.total_potential_savings:,.0f}

Top Missed Deductions:
{chr(10).join([f"- {d.section}: ₹{d.potential_saving:,.0f} ({d.description[:80]})" for d in deductions.missed_deductions[:3]])}

Top Investment Recommendation: {investments[0].instrument if investments else 'None'}

Write the personalised summary now.
"""
        summary = await llm_call(
            model=settings.EXPLAINER_MODEL,
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.5,
            max_tokens=500,
        )
        return summary.strip()

    except Exception as e:
        logger.error(f"Explainer Agent failed: {e}")
        return _template_summary(parsed_data, deductions, regime)


def _template_summary(
    data: ParsedFormData,
    deductions: DeductionResult,
    regime: RegimeComparison,
) -> str:
    total_save = regime.savings_with_recommended + deductions.total_potential_savings
    top_missed = deductions.missed_deductions[0] if deductions.missed_deductions else None

    lines = [
        f"🎉 Great news! You could save up to ₹{total_save:,.0f} in taxes this year!",
        "",
        f"Based on your salary of ₹{data.gross_salary:,.0f}, the **{regime.recommended_regime} Tax Regime** "
        f"is better for you — saving ₹{regime.savings_with_recommended:,.0f} right away.",
        "",
    ]

    if top_missed:
        lines.append(f"Your biggest missed opportunity is **Section {top_missed.section}** — "
                     f"{top_missed.description} This alone could save you ₹{top_missed.potential_saving:,.0f}.")
        lines.append("")

    lines.append(f"🎯 Priority Action: Switch to the {regime.recommended_regime} Regime when submitting "
                 f"your investment declaration to HR, and invest in the recommended instruments to maximise savings.")

    return "\n".join(lines)
