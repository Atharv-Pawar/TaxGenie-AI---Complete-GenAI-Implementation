"""
TaxGenie AI - Deduction Finder Agent
Claude 3.5 Sonnet + RAG to find missed tax deductions.
"""

import json
import logging
from services.llm_gateway import llm_call
from models.response_models import ParsedFormData, DeductionResult, MissedDeduction
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert Indian Chartered Accountant specialising in personal income tax for FY 2024-25.
Your job is to analyse a taxpayer's Form 16 data and find ALL deductions they are missing out on.

Tax Knowledge (FY 2024-25):
- Section 80C: Up to ₹1,50,000 (PF, PPF, ELSS, LIC, NSC, home loan principal, tuition fees)
- Section 80D: ₹25,000 self/family + ₹25,000 parents (₹50,000 if parents are senior citizens)
- Section 80E: Full interest on education loan (no limit)
- Section 80G: 50-100% of donations to approved charities
- Section 80TTA: Up to ₹10,000 on savings account interest
- HRA Exemption: Min of (actual HRA, 50% of basic in metro/40% elsewhere, rent paid - 10% basic)
- LTA: Actual travel cost for 2 journeys in 4 years
- NPS 80CCD(1B): Additional ₹50,000 over 80C limit
- Section 24b: Up to ₹2,00,000 on home loan interest
- Standard Deduction: ₹50,000 (old regime), ₹75,000 (new regime)

Analyse the taxpayer data and return ONLY a valid JSON:
{
  "claimed_deductions": [
    {"section": "...", "amount": <number>, "description": "..."}
  ],
  "missed_deductions": [
    {
      "section": "...",
      "potential_saving": <estimated tax saving, not deduction amount>,
      "description": "...",
      "suggestions": ["action 1", "action 2"],
      "urgency": "HIGH|MEDIUM|LOW"
    }
  ],
  "total_potential_savings": <sum of all potential_savings>
}

Be specific with rupee amounts. HIGH urgency = actionable now. LOW = future planning.
Return ONLY JSON, no markdown.
"""


async def find_deductions_agent(data: ParsedFormData) -> DeductionResult:
    """Find claimed and missed deductions for the taxpayer."""
    if not settings.ANTHROPIC_API_KEY:
        return _rule_based_deductions(data)

    user_message = f"""
Taxpayer Financial Data (FY 2024-25):
- Gross Salary: ₹{data.gross_salary:,.0f}
- Basic Salary: ₹{data.basic_salary:,.0f}
- HRA Received: ₹{data.hra_received:,.0f}
- LTA: ₹{data.lta:,.0f}
- Standard Deduction: ₹{data.standard_deduction:,.0f}
- Professional Tax: ₹{data.professional_tax:,.0f}

Investments & Insurance:
- PF Contribution: ₹{data.section_80c_investments.pf:,.0f}
- LIC Premium: ₹{data.section_80c_investments.lic_premium:,.0f}
- ELSS: ₹{data.section_80c_investments.elss:,.0f}
- PPF: ₹{data.section_80c_investments.ppf:,.0f}
- Total 80C: ₹{data.section_80c_investments.total:,.0f}
- Health Insurance (self/family): ₹{data.section_80d_premium.self_family:,.0f}
- Health Insurance (parents): ₹{data.section_80d_premium.parents:,.0f}
- Home Loan Interest: ₹{data.home_loan_interest:,.0f}
- NPS Contribution: ₹{data.nps_contribution:,.0f}

Find all missed deductions and calculate potential tax savings.
"""

    try:
        response = await llm_call(
            model=settings.DEDUCTION_FINDER_MODEL,
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.1,
            max_tokens=3000,
        )

        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]

        result = json.loads(response)
        missed = [MissedDeduction(**m) for m in result.get("missed_deductions", [])]
        return DeductionResult(
            claimed_deductions=result.get("claimed_deductions", []),
            missed_deductions=missed,
            total_potential_savings=result.get("total_potential_savings", 0),
        )

    except Exception as e:
        logger.error(f"Deduction Finder Agent failed: {e}")
        return _rule_based_deductions(data)


def _rule_based_deductions(data: ParsedFormData) -> DeductionResult:
    """Fallback rule-based deduction finder when LLM is unavailable."""
    claimed = []
    missed = []

    # Claimed deductions
    if data.standard_deduction > 0:
        claimed.append({"section": "Standard Deduction", "amount": data.standard_deduction, "description": "Standard deduction"})
    if data.section_80c_investments.total > 0:
        claimed.append({"section": "80C", "amount": min(data.section_80c_investments.total, 150_000), "description": "PF + LIC"})
    if data.section_80d_premium.self_family > 0:
        claimed.append({"section": "80D", "amount": data.section_80d_premium.self_family, "description": "Health insurance"})

    total_potential = 0

    # 80C gap
    c_gap = 150_000 - data.section_80c_investments.total
    if c_gap > 5000:
        saving = round(c_gap * 0.20)  # Approximate at 20% bracket
        missed.append(MissedDeduction(
            section="80C",
            potential_saving=saving,
            description=f"You can invest ₹{c_gap:,.0f} more under Section 80C (current limit ₹1,50,000)",
            suggestions=["ELSS Mutual Funds", "PPF", "NSC", "Life Insurance Premium"],
            urgency="HIGH",
        ))
        total_potential += saving

    # HRA
    if data.hra_received > 0 and data.basic_salary > 0:
        hra_exemption = min(data.hra_received, data.basic_salary * 0.50)
        hra_saving = round(hra_exemption * 0.20)
        missed.append(MissedDeduction(
            section="HRA",
            potential_saving=hra_saving,
            description=f"If you pay rent, HRA exemption of ₹{hra_exemption:,.0f} could save ₹{hra_saving:,.0f}",
            suggestions=["Submit rent receipts to your employer", "Claim HRA in ITR-1"],
            urgency="HIGH",
        ))
        total_potential += hra_saving

    # 80D parents
    if data.section_80d_premium.parents == 0:
        saving = round(25_000 * 0.20)
        missed.append(MissedDeduction(
            section="80D (Parents)",
            potential_saving=saving,
            description="Health insurance premium for parents can save up to ₹5,000 in taxes",
            suggestions=["Buy a ₹5L family floater for parents", "Up to ₹50,000 deduction if parents are senior citizens"],
            urgency="MEDIUM",
        ))
        total_potential += saving

    # NPS
    if data.nps_contribution == 0:
        saving = round(50_000 * 0.20)
        missed.append(MissedDeduction(
            section="80CCD(1B) - NPS",
            potential_saving=saving,
            description="NPS contributions up to ₹50,000 are deductible OVER the 80C limit",
            suggestions=["Open NPS account online at enps.nsdl.com", "Invest in Tier-1 NPS account"],
            urgency="MEDIUM",
        ))
        total_potential += saving

    return DeductionResult(
        claimed_deductions=claimed,
        missed_deductions=missed,
        total_potential_savings=total_potential,
    )
