# agents/investment_agent.py
"""
Investment Recommender Agent
Recommends tax-saving investments personalized to the user's
risk profile, income level, and missed deductions.
"""

import json
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an expert Indian financial advisor specializing
in tax-saving investments under Section 80C, 80CCD, 80D, etc.

Give concrete, personalized investment recommendations
based on the taxpayer's salary, unused deductions,
and risk appetite.

Return ONLY valid JSON — no markdown, no explanation.
""".strip()


RECOMMENDATION_PROMPT = """
Recommend tax-saving investments for this taxpayer.

## TAXPAYER PROFILE
Gross Salary:             ₹{gross_salary}
Remaining 80C Limit:      ₹{unused_80c}
Remaining 80CCD(1B) Limit:₹{unused_nps}
Remaining 80D Limit:      ₹{unused_80d}
Total Potential Saving:   ₹{total_saving}

## AVAILABLE INVESTMENT OPTIONS

### Under 80C (Limit: ₹1,50,000)
1. ELSS Mutual Fund  — 3-yr lock-in, market returns ~12-15%, High
2. PPF               — 15-yr lock-in, 7.1% guaranteed, Low
3. NSC               — 5-yr lock-in, 7.7% guaranteed, Low
4. Tax-Saving FD     — 5-yr lock-in, 6-7% bank rate, Low
5. SCSS              — 5-yr, 8.2%, only 60+ age, Low
6. LIC Premium       — Flexible, low risk, Low
7. Sukanya Samriddhi — For girl child, 8.2%, Low

### Under 80CCD(1B) — Extra ₹50,000
8. NPS Tier-1        — Market-linked, 10-12% historical, Medium

### Under 80D
9. Health Insurance  — Self: ₹25,000 | Parents: ₹25,000 extra

## YOUR TASK
Return a personalized list of 3-5 investment recommendations.

{{
  "recommendations": [
    {{
      "rank": 1,
      "section": "80C",
      "option": "Investment name",
      "amount_to_invest": number,
      "expected_tax_saving": number,
      "expected_return_percent": "string (e.g. 12-15% p.a.)",
      "risk_level": "Low | Medium | High",
      "lock_in_period": "string (e.g. 3 years)",
      "why_recommended": "Personalized reason for this taxpayer",
      "how_to_start": "Step-by-step on how to start",
      "platform": "Where to invest (e.g. Zerodha, HDFC, NSDL)",
      "suitable_for": "Who this is ideal for"
    }}
  ],
  "total_investment_suggested": number,
  "total_tax_saved": number,
  "quick_tip": "One-line most important advice"
}}
""".strip()


class InvestmentRecommenderAgent:
    """
    Recommends tax-saving investments using GPT-4.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def recommend(
        self,
        tax_data: dict,
        missed_deductions: list
    ) -> list[dict]:
        """
        Main entry point.
        Returns personalized investment recommendations.
        """
        logger.info("[InvestmentAgent] Generating recommendations")

        # Calculate unused limits
        deductions   = tax_data.get("deductions_chapter_vi_a", {})
        unused_80c   = max(0, 150_000 - deductions.get("section_80c", 0))
        unused_nps   = max(0,  50_000 - deductions.get("section_80ccd_1b", 0))
        unused_80d   = max(0,  25_000 - deductions.get("section_80d", 0))
        total_saving = sum(
            d.get("potential_tax_saving", 0) for d in missed_deductions
        )

        prompt = RECOMMENDATION_PROMPT.format(
            gross_salary = tax_data.get("gross_salary", 0),
            unused_80c   = unused_80c,
            unused_nps   = unused_nps,
            unused_80d   = unused_80d,
            total_saving = total_saving,
        )

        raw = await self._call_gpt4(prompt)
        return self._parse(raw)

    async def _call_gpt4(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model           = settings.PRIMARY_MODEL,
            temperature     = 0.3,
            max_tokens      = 3000,
            response_format = {"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def _parse(self, raw: str) -> list[dict]:
        data = self._safe_json(raw)
        recs = data.get("recommendations", [])

        if not recs:
            return self._fallback_recommendations()

        # Add quick tip as extra metadata on first item
        if recs and data.get("quick_tip"):
            recs[0]["quick_tip"] = data["quick_tip"]

        return recs

    def _fallback_recommendations(self) -> list[dict]:
        return [
            {
                "rank": 1,
                "section": "80C",
                "option": "ELSS Mutual Fund",
                "amount_to_invest": 150_000,
                "expected_tax_saving": 46_800,
                "expected_return_percent": "12-15% p.a.",
                "risk_level": "Medium",
                "lock_in_period": "3 years",
                "why_recommended": "Best combination of tax saving and wealth creation",
                "how_to_start": "Open account on Zerodha/Groww and invest in ELSS",
                "platform": "Zerodha, Groww, Kuvera",
                "suitable_for": "Taxpayers in 30% bracket",
            },
            {
                "rank": 2,
                "section": "80CCD(1B)",
                "option": "NPS Tier-1",
                "amount_to_invest": 50_000,
                "expected_tax_saving": 15_600,
                "expected_return_percent": "10-12% p.a.",
                "risk_level": "Medium",
                "lock_in_period": "Until retirement",
                "why_recommended": "Extra ₹50,000 deduction beyond 80C limit",
                "how_to_start": "Open NPS account on eNPS.nsdl.com",
                "platform": "NSDL eNPS",
                "suitable_for": "Salaried employees planning for retirement",
            },
        ]

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