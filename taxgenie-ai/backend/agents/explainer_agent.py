# agents/explainer_agent.py
"""
Explainer Agent
Generates plain-English, personalized tax summary using Claude.
Makes complex tax analysis easy to understand.
"""

import logging
import anthropic
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are TaxGenie, a friendly and knowledgeable Indian tax advisor.

Your job is to explain complex tax analysis in simple, 
encouraging, and actionable language.

Guidelines:
- Use simple English (no jargon)
- Use ₹ amounts throughout
- Be specific about recommended actions
- Sound like a trusted CA friend
- Keep it to 4-5 focused paragraphs
- End with 3 clear next steps
""".strip()


EXPLANATION_PROMPT = """
Generate a friendly, personalized tax summary for this taxpayer.

## ANALYSIS RESULTS

Gross Salary: ₹{gross_salary}
Recommended Regime: {recommended_regime}
Tax in Recommended Regime: ₹{recommended_tax}
Alternative Regime Tax: ₹{alt_tax}
Regime Savings: ₹{regime_savings}

Missed Deductions Found: {num_missed}
Total Additional Tax Savings Possible: ₹{total_savings}

Top Missed Opportunities:
{top_opportunities}

Top Investment Recommendations:
{top_investments}

## WRITE A SUMMARY THAT:

1. Opens with their biggest win (best regime + savings)
2. Highlights top 2-3 deductions they're missing (be specific)
3. Recommends 1-2 concrete investments to make immediately
4. Mentions the total potential savings clearly
5. Ends with 3 numbered action steps they should take before March 31

Keep it warm, personal, and actionable.
Do NOT use bullet points — write in flowing paragraphs.
End with:

**Your 3 Action Steps:**
1. ...
2. ...
3. ...
""".strip()


class ExplainerAgent:
    """
    Generates human-friendly explanations of tax analysis.
    Uses Claude for natural language quality.
    Falls back to GPT-4 if Claude unavailable.
    """

    def __init__(self):
        self.use_claude = bool(settings.ANTHROPIC_API_KEY)

        if self.use_claude:
            self.claude = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def explain(
        self,
        tax_data:          dict,
        missed_deductions: list,
        regime_comparison: dict,
        investments:       list,
    ) -> str:
        """
        Generate personalized explanation of complete tax analysis.
        """
        logger.info("[ExplainerAgent] Generating explanation")

        comparison   = regime_comparison.get("comparison",    {})
        recommendation = regime_comparison.get("recommendation", {})

        better_regime  = recommendation.get("regime", "NEW")
        old_tax        = comparison.get("old_regime_tax", 0)
        new_tax        = comparison.get("new_regime_tax", 0)
        regime_savings = comparison.get("savings_amount", 0)

        recommended_tax = old_tax if better_regime == "OLD" else new_tax
        alt_tax         = new_tax if better_regime == "OLD" else old_tax
        total_savings   = sum(d.get("potential_tax_saving", 0) for d in missed_deductions)

        # Format top missed deductions
        top_missed = missed_deductions[:3]
        top_opp_text = "\n".join(
            f"- {o.get('section', '')}: Save ₹{o.get('potential_tax_saving', 0):,.0f} "
            f"({o.get('description', '')})"
            for o in top_missed
        )

        # Format top investments
        top_inv = investments[:2]
        top_inv_text = "\n".join(
            f"- {i.get('option', '')}: Invest ₹{i.get('amount_to_invest', 0):,.0f} "
            f"→ Save ₹{i.get('expected_tax_saving', 0):,.0f}"
            for i in top_inv
        )

        prompt = EXPLANATION_PROMPT.format(
            gross_salary       = tax_data.get("gross_salary", 0),
            recommended_regime = better_regime,
            recommended_tax    = f"{recommended_tax:,.0f}",
            alt_tax            = f"{alt_tax:,.0f}",
            regime_savings     = f"{regime_savings:,.0f}",
            num_missed         = len(missed_deductions),
            total_savings      = f"{total_savings:,.0f}",
            top_opportunities  = top_opp_text or "None found",
            top_investments    = top_inv_text  or "None found",
        )

        if self.use_claude:
            return await self._call_claude(prompt)
        return await self._call_gpt4(prompt)

    async def _call_claude(self, prompt: str) -> str:
        response = await self.claude.messages.create(
            model      = settings.CLAUDE_MODEL,
            max_tokens = 1500,
            system     = SYSTEM_PROMPT,
            messages   = [{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def _call_gpt4(self, prompt: str) -> str:
        response = await self.openai.chat.completions.create(
            model       = settings.PRIMARY_MODEL,
            temperature = 0.7,
            max_tokens  = 1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        return response.choices[0].message.content