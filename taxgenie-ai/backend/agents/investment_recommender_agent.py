"""
TaxGenie AI - Investment Recommender Agent
GPT-4o powered personalised tax-saving investment recommendations.
"""

import json
import logging
from services.llm_gateway import llm_call
from models.response_models import (
    ParsedFormData, RegimeComparison, InvestmentRecommendation, RiskProfile
)
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a SEBI-registered financial advisor specialising in tax-saving investments in India.
Based on a taxpayer's financial profile, recommend personalised tax-saving investments.

Return ONLY a JSON array of investment recommendations:
[
  {
    "instrument": "ELSS Mutual Funds",
    "section": "80C",
    "recommended_amount": 46800,
    "expected_returns": "12-15% CAGR (historical)",
    "lock_in_period": "3 years (shortest among 80C)",
    "risk_level": "Moderate-High",
    "reason": "Best tax-saving instrument with equity exposure and shortest lock-in",
    "top_picks": ["Axis ELSS Tax Saver Fund", "Mirae Asset Tax Saver Fund", "Quant Tax Plan"]
  }
]

Rules:
- Only recommend if they have a real tax benefit (regime matters!)
- Match recommendations to risk profile
- Include 3-5 specific recommendations
- Amounts must be actionable (fill the gap in 80C first, then NPS, etc.)
- For New Regime taxpayers, focus on wealth building since most deductions are irrelevant
- Return ONLY the JSON array, no markdown
"""


async def investment_recommender_agent(
    data: ParsedFormData,
    regime: RegimeComparison,
    risk_profile: RiskProfile = RiskProfile.MODERATE,
) -> list[InvestmentRecommendation]:
    """Generate personalised investment recommendations."""
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        return _rule_based_recommendations(data, regime, risk_profile)

    model = settings.INVESTMENT_MODEL if settings.OPENAI_API_KEY else settings.CHAT_MODEL
    c_gap = max(0, 150_000 - data.section_80c_investments.total)

    user_message = f"""
Taxpayer Profile:
- Annual Gross Salary: ₹{data.gross_salary:,.0f}
- Recommended Tax Regime: {regime.recommended_regime}
- Risk Profile: {risk_profile.value.capitalize()}
- Current 80C Investments: ₹{data.section_80c_investments.total:,.0f} (gap: ₹{c_gap:,.0f})
- NPS Contribution: ₹{data.nps_contribution:,.0f}
- Health Insurance (self): ₹{data.section_80d_premium.self_family:,.0f}
- Health Insurance (parents): ₹{data.section_80d_premium.parents:,.0f}
- Tax Savings Available: ₹{regime.savings_with_recommended:,.0f} already; potential additional ₹{0:,.0f} with better planning

Generate personalised investment recommendations to maximise tax savings.
"""

    try:
        response = await llm_call(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.2,
            max_tokens=2000,
        )

        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]

        raw_list = json.loads(response)
        return [InvestmentRecommendation(**item) for item in raw_list]

    except Exception as e:
        logger.error(f"Investment Recommender failed: {e}")
        return _rule_based_recommendations(data, regime, risk_profile)


def _rule_based_recommendations(
    data: ParsedFormData,
    regime: RegimeComparison,
    risk_profile: RiskProfile,
) -> list[InvestmentRecommendation]:
    """Fallback rule-based recommendations."""
    recs = []
    c_gap = max(0, 150_000 - data.section_80c_investments.total)

    if regime.recommended_regime == "OLD" and c_gap > 0:
        if risk_profile == RiskProfile.AGGRESSIVE:
            recs.append(InvestmentRecommendation(
                instrument="ELSS Mutual Funds",
                section="80C",
                recommended_amount=min(c_gap, 150_000),
                expected_returns="12-15% CAGR (historical)",
                lock_in_period="3 years",
                risk_level="Moderate-High",
                reason=f"Fill your ₹{c_gap:,.0f} 80C gap with equity ELSS for highest returns + tax saving",
                top_picks=["Axis ELSS Tax Saver", "Mirae Asset Tax Saver", "Quant Tax Plan"],
            ))
        elif risk_profile == RiskProfile.MODERATE:
            recs.append(InvestmentRecommendation(
                instrument="ELSS Mutual Funds",
                section="80C",
                recommended_amount=round(min(c_gap, 150_000) * 0.6),
                expected_returns="12-14% CAGR",
                lock_in_period="3 years",
                risk_level="Moderate-High",
                reason="Best combination of returns and tax saving for moderate risk investors",
                top_picks=["Mirae Asset Tax Saver", "Canara Robeco Equity Tax Saver"],
            ))
            recs.append(InvestmentRecommendation(
                instrument="PPF (Public Provident Fund)",
                section="80C",
                recommended_amount=round(min(c_gap, 150_000) * 0.4),
                expected_returns="7.1% p.a. (tax-free)",
                lock_in_period="15 years (partial withdrawal from 7th year)",
                risk_level="Low",
                reason="Safe, tax-free returns for capital preservation",
                top_picks=["Any nationalised bank or Post Office"],
            ))
        else:
            recs.append(InvestmentRecommendation(
                instrument="PPF (Public Provident Fund)",
                section="80C",
                recommended_amount=min(c_gap, 150_000),
                expected_returns="7.1% p.a. (tax-free)",
                lock_in_period="15 years",
                risk_level="Low",
                reason="Safest 80C option with guaranteed government-backed returns",
                top_picks=["SBI PPF Account", "Post Office PPF"],
            ))

    # NPS recommendation
    if data.nps_contribution == 0:
        recs.append(InvestmentRecommendation(
            instrument="NPS (National Pension System)",
            section="80CCD(1B)",
            recommended_amount=50_000,
            expected_returns="8-10% CAGR (market-linked)",
            lock_in_period="Till retirement (partial withdrawal allowed)",
            risk_level="Moderate",
            reason="Extra ₹50,000 deduction over 80C limit. Can save ₹10,000+ in taxes.",
            top_picks=["HDFC Pension Fund", "SBI Pension Fund", "ICICI Prudential Pension Fund"],
        ))

    # Health insurance for parents
    if data.section_80d_premium.parents == 0:
        recs.append(InvestmentRecommendation(
            instrument="Health Insurance for Parents",
            section="80D",
            recommended_amount=25_000,
            expected_returns="Protection against medical expenses",
            lock_in_period="Annual renewal",
            risk_level="Low",
            reason="Protect parents + save up to ₹5,000 in tax",
            top_picks=["Star Health Senior Citizen Red Carpet", "Niva Bupa ReAssure 2.0", "Care Senior"],
        ))

    return recs
