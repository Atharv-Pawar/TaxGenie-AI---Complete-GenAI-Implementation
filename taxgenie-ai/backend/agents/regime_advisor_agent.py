"""
TaxGenie AI - Regime Advisor Agent
Combines deterministic Python tax math with GPT-4o explanation.
"""

import logging
from services.tax_calculator import compare_regimes
from services.llm_gateway import llm_call
from models.response_models import ParsedFormData, RegimeComparison
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a senior Indian tax advisor. A taxpayer has asked which tax regime is better for them.
You have been given the mathematical calculation results. Provide a clear, personalised 2-3 sentence
explanation of why one regime is recommended over the other. Include specific numbers.
Write in plain English, empathetically, as if talking to someone who finds tax confusing.
"""


async def regime_advisor_agent(data: ParsedFormData) -> RegimeComparison:
    """
    Calculate Old vs New Regime comparison and generate a human explanation.
    """
    # Always do deterministic math first
    comparison = compare_regimes(data)

    if not settings.OPENAI_API_KEY:
        return comparison

    try:
        user_message = f"""
Taxpayer: Gross salary ₹{data.gross_salary:,.0f}, total deductions ₹{comparison.old_regime.total_deductions:,.0f}

OLD REGIME:
  Taxable Income: ₹{comparison.old_regime.taxable_income:,.0f}
  Total Tax: ₹{comparison.old_regime.total_tax:,.0f}

NEW REGIME:
  Taxable Income: ₹{comparison.new_regime.taxable_income:,.0f}
  Total Tax: ₹{comparison.new_regime.total_tax:,.0f}

Recommended: {comparison.recommended_regime} REGIME
Savings: ₹{comparison.savings_with_recommended:,.0f}
Breakeven deductions needed for Old Regime: ₹{comparison.breakeven_deduction_amount:,.0f}

Write a personalised 2-3 sentence recommendation.
"""
        explanation = await llm_call(
            model=settings.REGIME_ADVISOR_MODEL,
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.3,
            max_tokens=300,
        )
        comparison.recommendation_reason = explanation.strip()

    except Exception as e:
        logger.error(f"Regime explanation failed (math still valid): {e}")

    return comparison
