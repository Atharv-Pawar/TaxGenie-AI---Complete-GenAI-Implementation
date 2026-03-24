# agents/deduction_agent.py
"""
Deduction Finder Agent
Uses Claude 3.5 Sonnet + RAG (tax knowledge base)
to identify all missed tax-saving opportunities.
"""

import json
import logging
from typing import Any

import anthropic
from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a senior Indian Chartered Accountant (CA) specializing
in income tax planning for salaried individuals.

Your role:
- Identify every tax deduction the taxpayer is NOT fully utilizing
- Calculate exact tax savings possible for each missed deduction
- Prioritize opportunities by impact (highest saving first)
- Give specific, actionable investment/expense recommendations

Tax Year: FY 2024-25 (AY 2025-26)
Always apply 4% Health & Education Cess on top of tax savings.
Return ONLY valid JSON — no markdown, no explanation text.
""".strip()


ANALYSIS_PROMPT = """
Analyze this taxpayer's data and find ALL missed deductions.

## TAXPAYER DATA
Gross Salary:           ₹{gross_salary}
HRA Received:           ₹{hra}
LTA Received:           ₹{lta}
Professional Tax:       ₹{professional_tax}

Current Deductions Claimed:
  80C (PPF/ELSS/LIC):  ₹{section_80c}  (Limit: ₹1,50,000)
  80CCD(1B) NPS:        ₹{section_80ccd_1b}  (Limit: ₹50,000)
  80D Health Insurance: ₹{section_80d}  (Limit: ₹25,000-₹1,00,000)
  80E Education Loan:   ₹{section_80e}  (No limit)
  80G Donations:        ₹{section_80g}
  80TTA Savings Int:    ₹{section_80tta} (Limit: ₹10,000)
  Home Loan Interest:   ₹{home_loan_interest} (Limit: ₹2,00,000)
  Standard Deduction:   ₹{standard_deduction}

## TAX RATE CONTEXT
Approximate tax bracket for this income:
- Up to ₹5L:   5% + 4% cess = 5.2%
- ₹5L-₹10L:   20% + 4% cess = 20.8%
- Above ₹10L: 30% + 4% cess = 31.2%

## DEDUCTION LIMITS REFERENCE (FY 2024-25)
- 80C:        ₹1,50,000 (PPF, ELSS, LIC, NSC, Tax FD, Home Loan Principal)
- 80CCD(1B):  ₹50,000   (NPS — additional, over & above 80C)
- 80D Self:   ₹25,000   (₹50,000 if senior citizen)
- 80D Parents:₹25,000   (₹50,000 if parents are senior)
- 80TTA:      ₹10,000   (savings account interest)
- 80E:        No limit  (education loan interest)
- Sec 24(b):  ₹2,00,000 (home loan interest — self occupied)
- 80G:        Varies    (50% or 100% depending on organization)

## YOUR TASK
For each missed opportunity, return a JSON object in this exact format:

{{
  "opportunities": [
    {{
      "section": "80C",
      "description": "One-line description",
      "current_claimed": number,
      "max_limit": number,
      "unused_limit": number,
      "potential_tax_saving": number,
      "tax_rate_applied": "string (e.g. 30% + 4% cess = 31.2%)",
      "priority": "HIGH | MEDIUM | LOW",
      "recommended_options": [
        {{
          "option": "Investment/expense name",
          "details": "Why this is good for this taxpayer",
          "risk": "Low | Medium | High",
          "lock_in": "string (e.g. 3 years)"
        }}
      ],
      "action_steps": [
        "Step 1...",
        "Step 2..."
      ],
      "deadline": "March 31, 2025"
    }}
  ],
  "total_potential_savings": number,
  "top_priority_action": "string — single most impactful thing to do now"
}}

Only include sections where unused_limit > 0.
Sort by potential_tax_saving descending.
""".strip()


# ── Agent Class ───────────────────────────────────────────────────────────────

class DeductionFinderAgent:
    """
    Finds all missed tax deductions using Claude 3.5 Sonnet.
    Falls back to GPT-4 if Anthropic key is unavailable.
    """

    def __init__(self):
        self.use_claude = bool(settings.ANTHROPIC_API_KEY)

        if self.use_claude:
            self.claude = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
            logger.info("[DeductionAgent] Using Claude 3.5 Sonnet")
        else:
            self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("[DeductionAgent] Using GPT-4 (Claude key not set)")

    # ── Public API ────────────────────────────────────────────────────────────

    async def analyze(self, tax_data: dict) -> list[dict[str, Any]]:
        """
        Main entry point.
        Returns a list of missed deduction opportunities sorted by impact.
        """
        logger.info("[DeductionAgent] Starting deduction analysis")

        # Extract values
        deductions = tax_data.get("deductions_chapter_vi_a", {})
        exemptions = tax_data.get("exemptions_section_10", {})

        prompt = ANALYSIS_PROMPT.format(
            gross_salary        = tax_data.get("gross_salary", 0),
            hra                 = exemptions.get("hra", 0),
            lta                 = exemptions.get("lta", 0),
            professional_tax    = tax_data.get("professional_tax", 0),
            section_80c         = deductions.get("section_80c", 0),
            section_80ccd_1b    = deductions.get("section_80ccd_1b", 0),
            section_80d         = deductions.get("section_80d", 0),
            section_80e         = deductions.get("section_80e", 0),
            section_80g         = deductions.get("section_80g", 0),
            section_80tta       = deductions.get("section_80tta", 0),
            home_loan_interest  = tax_data.get("income_from_house_property", 0),
            standard_deduction  = tax_data.get("standard_deduction", 50000),
        )

        # Call LLM
        raw = await self._call_llm(prompt)

        # Parse & validate
        opportunities = self._parse_response(raw, tax_data)

        logger.info(
            f"[DeductionAgent] Found {len(opportunities)} opportunities | "
            f"Total saving: ₹{sum(o.get('potential_tax_saving', 0) for o in opportunities):,.0f}"
        )

        return opportunities

    # ── LLM Calls ─────────────────────────────────────────────────────────────

    async def _call_llm(self, prompt: str) -> str:
        """
        Call Claude or GPT-4 depending on available keys.
        """
        if self.use_claude:
            return await self._call_claude(prompt)
        return await self._call_gpt4(prompt)

    async def _call_claude(self, prompt: str) -> str:
        """
        Call Anthropic Claude 3.5 Sonnet.
        """
        response = await self.claude.messages.create(
            model      = settings.CLAUDE_MODEL,
            max_tokens = 4096,
            system     = SYSTEM_PROMPT,
            messages   = [{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def _call_gpt4(self, prompt: str) -> str:
        """
        Fallback: Call OpenAI GPT-4.
        """
        response = await self.openai.chat.completions.create(
            model           = settings.PRIMARY_MODEL,
            temperature     = 0.2,
            max_tokens      = 4096,
            response_format = {"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        return response.choices[0].message.content

    # ── Parsing & Validation ──────────────────────────────────────────────────

    def _parse_response(self, raw: str, tax_data: dict) -> list[dict]:
        """
        Parse the LLM JSON response into a clean list of opportunities.
        Re-calculates tax savings to ensure accuracy.
        """
        data = self._safe_json(raw)
        opportunities = data.get("opportunities", [])

        if not isinstance(opportunities, list):
            logger.warning("[DeductionAgent] Unexpected response format")
            return self._fallback_opportunities(tax_data)

        gross = tax_data.get("gross_salary", 0)
        rate  = self._get_tax_rate(gross)

        validated = []
        for opp in opportunities:
            unused = float(opp.get("unused_limit", 0))
            if unused <= 0:
                continue

            # Recalculate saving with correct rate
            opp["potential_tax_saving"] = round(unused * rate, 2)
            opp["tax_rate_applied"]     = f"{rate*100:.1f}% (incl. cess)"

            # Ensure required keys
            opp.setdefault("recommended_options", [])
            opp.setdefault("action_steps", [])
            opp.setdefault("priority",     "MEDIUM")
            opp.setdefault("deadline",     "March 31, 2025")

            validated.append(opp)

        # Sort by saving, highest first
        validated.sort(key=lambda x: x.get("potential_tax_saving", 0), reverse=True)

        return validated

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_tax_rate(self, gross_salary: float) -> float:
        """
        Effective marginal rate including 4% cess.
        """
        if gross_salary <= 500_000:
            return 0.05 * 1.04   # 5.20%
        elif gross_salary <= 1_000_000:
            return 0.20 * 1.04   # 20.80%
        else:
            return 0.30 * 1.04   # 31.20%

    def _fallback_opportunities(self, tax_data: dict) -> list[dict]:
        """
        Return basic hardcoded opportunities if LLM fails.
        """
        gross    = tax_data.get("gross_salary", 0)
        rate     = self._get_tax_rate(gross)
        deductions = tax_data.get("deductions_chapter_vi_a", {})

        opportunities = []

        # 80C
        current_80c = deductions.get("section_80c", 0)
        if current_80c < 150_000:
            unused = 150_000 - current_80c
            opportunities.append({
                "section":              "80C",
                "description":          "Invest in PPF/ELSS/LIC to save tax",
                "current_claimed":      current_80c,
                "max_limit":            150_000,
                "unused_limit":         unused,
                "potential_tax_saving": round(unused * rate, 2),
                "priority":             "HIGH",
                "recommended_options":  [
                    {"option": "ELSS", "details": "3-year lock-in, market returns", "risk": "Medium"},
                    {"option": "PPF",  "details": "Safe, 15-year, 7.1% p.a.",      "risk": "Low"},
                ],
                "action_steps":["Open ELSS/PPF account", "Invest remaining limit"],
                "deadline": "March 31, 2025",
            })

        # 80CCD(1B)
        current_nps = deductions.get("section_80ccd_1b", 0)
        if current_nps < 50_000:
            unused = 50_000 - current_nps
            opportunities.append({
                "section":              "80CCD(1B)",
                "description":          "Additional NPS contribution — extra ₹50,000 deduction",
                "current_claimed":      current_nps,
                "max_limit":            50_000,
                "unused_limit":         unused,
                "potential_tax_saving": round(unused * rate, 2),
                "priority":             "HIGH",
                "recommended_options":  [
                    {"option": "NPS Tier-1", "details": "Open NPS Tier-1 account", "risk": "Medium"},
                ],
                "action_steps":["Open NPS Tier-1 account online", "Contribute ₹50,000 before March 31"],
                "deadline": "March 31, 2025",
            })

        return opportunities

    def _safe_json(self, text: str) -> dict:
        """
        Parse JSON safely from LLM text output.
        """
        if not text:
            return {}

        # Remove markdown fences
        for fence in ("```json", "```"):
            if fence in text:
                text = text.split(fence)[-1].split("```")[0]

        # Find the outermost JSON object
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"[DeductionAgent] JSON parse error: {e}")
            return {}