# agents/regime_agent.py
"""
Tax Regime Advisor Agent
Compares Old vs New tax regime using GPT-4 with precise calculations.
"""

import json
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert Indian tax consultant.
Calculate exact income tax under both Old and New regime for FY 2024-25.
Be mathematically precise. Show all slab calculations.
Return ONLY valid JSON — no markdown, no explanation.
""".strip()


COMPARISON_PROMPT = """
Compare Old vs New tax regime for this taxpayer.

## TAXPAYER DATA
Gross Salary:         ₹{gross_salary}

Deductions (Old Regime only):
  Standard Deduction: ₹{standard_deduction} (max ₹50,000 old / ₹75,000 new)
  Section 80C:        ₹{section_80c}
  Section 80CCD(1B):  ₹{section_80ccd_1b}
  Section 80D:        ₹{section_80d}
  Home Loan Interest: ₹{home_loan_interest}
  HRA Exemption:      ₹{hra_exemption}
  LTA Exemption:      ₹{lta_exemption}
  Professional Tax:   ₹{professional_tax}

## TAX SLAB RULES FY 2024-25

### OLD REGIME (Slabs)
| Income Range         | Rate |
|----------------------|------|
| 0 – 2,50,000         |  0%  |
| 2,50,001 – 5,00,000  |  5%  |
| 5,00,001 – 10,00,000 | 20%  |
| Above 10,00,000      | 30%  |

Rebate 87A: Full rebate if taxable income ≤ ₹5,00,000

### NEW REGIME (Slabs)
| Income Range           | Rate |
|------------------------|------|
| 0 – 3,00,000           |  0%  |
| 3,00,001 – 7,00,000    |  5%  |
| 7,00,001 – 10,00,000   | 10%  |
| 10,00,001 – 12,00,000  | 15%  |
| 12,00,001 – 15,00,000  | 20%  |
| Above 15,00,000        | 30%  |

Standard Deduction (New): ₹75,000
Rebate 87A: Full rebate if taxable income ≤ ₹7,00,000

### CESS
4% Health & Education Cess on (Tax + Surcharge)

## RETURN THIS JSON
{{
  "old_regime": {{
    "gross_income": number,
    "deductions_breakdown": {{
      "standard_deduction": number,
      "section_80c": number,
      "section_80ccd_1b": number,
      "section_80d": number,
      "home_loan_interest": number,
      "hra_exemption": number,
      "lta_exemption": number,
      "professional_tax": number,
      "total": number
    }},
    "taxable_income": number,
    "slab_tax_breakdown": {{
      "slab_0_250k":    {{"on": number, "rate": "0%",  "tax": 0}},
      "slab_250k_500k": {{"on": number, "rate": "5%",  "tax": number}},
      "slab_500k_1m":   {{"on": number, "rate": "20%", "tax": number}},
      "slab_above_1m":  {{"on": number, "rate": "30%", "tax": number}}
    }},
    "gross_tax": number,
    "rebate_87a": number,
    "tax_after_rebate": number,
    "cess_4_percent": number,
    "total_tax": number
  }},
  "new_regime": {{
    "gross_income": number,
    "deductions_breakdown": {{
      "standard_deduction": 75000,
      "total": 75000
    }},
    "taxable_income": number,
    "slab_tax_breakdown": {{
      "slab_0_300k":    {{"on": number, "rate": "0%",  "tax": 0}},
      "slab_300k_700k": {{"on": number, "rate": "5%",  "tax": number}},
      "slab_700k_1m":   {{"on": number, "rate": "10%", "tax": number}},
      "slab_1m_1200k":  {{"on": number, "rate": "15%", "tax": number}},
      "slab_1200k_1500k":{{"on": number, "rate": "20%", "tax": number}},
      "slab_above_1500k":{{"on": number, "rate": "30%", "tax": number}}
    }},
    "gross_tax": number,
    "rebate_87a": number,
    "tax_after_rebate": number,
    "cess_4_percent": number,
    "total_tax": number
  }},
  "comparison": {{
    "old_regime_tax": number,
    "new_regime_tax": number,
    "difference": number,
    "better_regime": "OLD | NEW | SAME",
    "savings_amount": number,
    "savings_percentage": number
  }},
  "recommendation": {{
    "regime": "OLD | NEW",
    "confidence": "HIGH | MEDIUM | LOW",
    "primary_reason": "string",
    "detailed_reasoning": ["reason1", "reason2", "reason3"],
    "breakeven_total_deductions": number,
    "your_total_deductions": number
  }}
}}
""".strip()


# ── Agent Class ───────────────────────────────────────────────────────────────

class RegimeAdvisorAgent:
    """
    Compares Old vs New tax regime with detailed calculations.
    Uses GPT-4 with programmatic fallback for accuracy.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # ── Public API ────────────────────────────────────────────────────────────

    async def compare(self, tax_data: dict) -> dict:
        """
        Main entry point.
        Returns full regime comparison with recommendation.
        """
        logger.info("[RegimeAgent] Starting regime comparison")

        deductions = tax_data.get("deductions_chapter_vi_a", {})
        exemptions = tax_data.get("exemptions_section_10", {})

        prompt = COMPARISON_PROMPT.format(
            gross_salary        = tax_data.get("gross_salary", 0),
            standard_deduction  = tax_data.get("standard_deduction", 50000),
            section_80c         = min(deductions.get("section_80c", 0), 150_000),
            section_80ccd_1b    = min(deductions.get("section_80ccd_1b", 0), 50_000),
            section_80d         = min(deductions.get("section_80d", 0), 100_000),
            home_loan_interest  = min(tax_data.get("income_from_house_property", 0), 200_000),
            hra_exemption       = exemptions.get("hra", 0),
            lta_exemption       = exemptions.get("lta", 0),
            professional_tax    = tax_data.get("professional_tax", 0),
        )

        # Call GPT-4
        raw = await self._call_gpt4(prompt)
        ai_result = self._safe_json(raw)

        # Always cross-validate with deterministic calculation
        calculated = self._calculate_deterministic(tax_data)

        # Merge: prefer calculated numbers, AI reasoning
        result = self._merge(calculated, ai_result)

        logger.info(
            f"[RegimeAgent] Old: ₹{result['comparison']['old_regime_tax']:,.0f} | "
            f"New: ₹{result['comparison']['new_regime_tax']:,.0f} | "
            f"Better: {result['comparison']['better_regime']}"
        )

        return result

    # ── LLM Call ─────────────────────────────────────────────────────────────

    async def _call_gpt4(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model           = settings.PRIMARY_MODEL,
            temperature     = 0.1,
            max_tokens      = 3000,
            response_format = {"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        return response.choices[0].message.content

    # ── Deterministic Calculation (Ground Truth) ──────────────────────────────

    def _calculate_deterministic(self, tax_data: dict) -> dict:
        """
        Mathematically correct tax calculation for both regimes.
        This is the source of truth for numbers.
        """
        gross      = tax_data.get("gross_salary", 0)
        deductions = tax_data.get("deductions_chapter_vi_a", {})
        exemptions = tax_data.get("exemptions_section_10", {})

        # ── OLD REGIME ──────────────────────────────────────
        old_deductions = (
            min(tax_data.get("standard_deduction", 50_000), 50_000) +
            min(deductions.get("section_80c",      0), 150_000)     +
            min(deductions.get("section_80ccd_1b", 0),  50_000)     +
            min(deductions.get("section_80d",      0), 100_000)     +
            min(tax_data.get("income_from_house_property", 0), 200_000) +
            exemptions.get("hra", 0)                                 +
            exemptions.get("lta", 0)                                 +
            tax_data.get("professional_tax", 0)
        )

        old_taxable = max(0, gross - old_deductions)
        old_tax     = self._slab_tax_old(old_taxable)
        old_tax     = self._rebate_87a(old_tax, old_taxable, "old")
        old_cess    = old_tax * 0.04
        old_total   = round(old_tax + old_cess, 2)

        # ── NEW REGIME ──────────────────────────────────────
        new_std      = 75_000
        new_taxable  = max(0, gross - new_std)
        new_tax      = self._slab_tax_new(new_taxable)
        new_tax      = self._rebate_87a(new_tax, new_taxable, "new")
        new_cess     = new_tax * 0.04
        new_total    = round(new_tax + new_cess, 2)

        # ── COMPARISON ──────────────────────────────────────
        if old_total < new_total:
            better  = "OLD"
            savings = new_total - old_total
        elif new_total < old_total:
            better  = "NEW"
            savings = old_total - new_total
        else:
            better  = "SAME"
            savings = 0

        savings_pct = round((savings / max(old_total, new_total, 1)) * 100, 1)

        return {
            "old_regime": {
                "gross_income":       gross,
                "total_deductions":   old_deductions,
                "taxable_income":     old_taxable,
                "gross_tax":          round(old_tax, 2),
                "cess_4_percent":     round(old_cess, 2),
                "total_tax":          old_total,
            },
            "new_regime": {
                "gross_income":      gross,
                "total_deductions":  new_std,
                "taxable_income":    new_taxable,
                "gross_tax":         round(new_tax, 2),
                "cess_4_percent":    round(new_cess, 2),
                "total_tax":         new_total,
            },
            "comparison": {
                "old_regime_tax":    old_total,
                "new_regime_tax":    new_total,
                "difference":        round(abs(old_total - new_total), 2),
                "better_regime":     better,
                "savings_amount":    round(savings, 2),
                "savings_percentage":savings_pct,
            },
        }

    def _slab_tax_old(self, income: float) -> float:
        """Old regime slab tax."""
        tax = 0.0
        slabs = [
            (250_000,        0.00),
            (500_000,        0.05),
            (1_000_000,      0.20),
            (float("inf"),   0.30),
        ]
        prev = 0
        for limit, rate in slabs:
            if income <= prev:
                break
            taxable = min(income, limit) - prev
            tax    += taxable * rate
            prev    = limit
        return tax

    def _slab_tax_new(self, income: float) -> float:
        """New regime slab tax."""
        tax = 0.0
        slabs = [
            (300_000,        0.00),
            (700_000,        0.05),
            (1_000_000,      0.10),
            (1_200_000,      0.15),
            (1_500_000,      0.20),
            (float("inf"),   0.30),
        ]
        prev = 0
        for limit, rate in slabs:
            if income <= prev:
                break
            taxable = min(income, limit) - prev
            tax    += taxable * rate
            prev    = limit
        return tax

    def _rebate_87a(self, tax: float, taxable: float, regime: str) -> float:
        """Apply Section 87A rebate."""
        if regime == "new" and taxable <= 700_000:
            return 0.0
        if regime == "old" and taxable <= 500_000:
            return max(0.0, tax - 12_500)
        return tax

    # ── Merge AI + Calculated ─────────────────────────────────────────────────

    def _merge(self, calculated: dict, ai_result: dict) -> dict:
        """
        Use calculated numbers (reliable) + AI recommendation (richer).
        """
        result = calculated.copy()

        if "recommendation" in ai_result:
            result["recommendation"] = ai_result["recommendation"]
        else:
            better  = calculated["comparison"]["better_regime"]
            savings = calculated["comparison"]["savings_amount"]
            result["recommendation"] = {
                "regime":     better,
                "confidence": "HIGH" if savings > 5_000 else "MEDIUM",
                "primary_reason": (
                    f"{better} regime saves ₹{savings:,.0f} for this income level."
                ),
                "detailed_reasoning": [
                    f"Total deductions in old regime: ₹{calculated['old_regime']['total_deductions']:,.0f}",
                    f"Standard deduction in new regime: ₹75,000 only",
                    f"Difference: ₹{savings:,.0f} in favor of {better} regime",
                ],
            }

        return result

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _safe_json(self, text: str) -> dict:
        if not text:
            return {}
        for fence in ("```json", "```"):
            if fence in text:
                text = text.split(fence)[-1].split("```")[0]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {}