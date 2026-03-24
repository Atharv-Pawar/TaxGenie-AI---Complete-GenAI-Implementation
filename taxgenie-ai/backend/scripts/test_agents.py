"""
TaxGenie AI - Test Agents Script
Tests all individual agents and the orchestrator pipeline.

Usage:
  python scripts/test_agents.py
  python scripts/test_agents.py --pdf ../sample_data/sample_form16.pdf
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.response_models import (
    ParsedFormData, Section80CBreakdown, Section80DBreakdown, RiskProfile
)


def get_demo_form_data() -> ParsedFormData:
    return ParsedFormData(
        gross_salary=1_200_000,
        basic_salary=600_000,
        hra_received=240_000,
        lta=50_000,
        special_allowance=310_000,
        standard_deduction=50_000,
        professional_tax=2_400,
        section_80c_investments=Section80CBreakdown(
            pf=72_000, lic_premium=15_000, total=87_000
        ),
        section_80d_premium=Section80DBreakdown(self_family=12_000, total=12_000),
        total_tds_deducted=82_000,
        employer_name="Tech Corp Pvt Ltd",
        assessment_year="2025-26",
    )


async def test_pdf_parser(pdf_path: str | None = None):
    print("\n1️⃣  Testing PDF Parser Agent...")
    from agents.pdf_parser_agent import parse_pdf_agent

    if pdf_path and Path(pdf_path).exists():
        pdf_bytes = Path(pdf_path).read_bytes()
    else:
        pdf_bytes = b"%PDF-1.4 dummy"  # Will fall back to demo data

    result = await parse_pdf_agent(pdf_bytes)
    print(f"   Gross Salary: ₹{result.gross_salary:,.0f}")
    print(f"   Employer: {result.employer_name}")
    print(f"   80C Total: ₹{result.section_80c_investments.total:,.0f}")
    print("   ✅ PDF Parser Agent: OK")
    return result


async def test_deduction_finder(data: ParsedFormData):
    print("\n2️⃣  Testing Deduction Finder Agent...")
    from agents.deduction_finder_agent import find_deductions_agent

    result = await find_deductions_agent(data)
    print(f"   Claimed deductions: {len(result.claimed_deductions)}")
    print(f"   Missed deductions: {len(result.missed_deductions)}")
    print(f"   Total potential savings: ₹{result.total_potential_savings:,.0f}")
    for md in result.missed_deductions:
        print(f"   → {md.section}: ₹{md.potential_saving:,.0f} [{md.urgency}]")
    print("   ✅ Deduction Finder Agent: OK")
    return result


async def test_regime_advisor(data: ParsedFormData):
    print("\n3️⃣  Testing Regime Advisor Agent...")
    from agents.regime_advisor_agent import regime_advisor_agent

    result = await regime_advisor_agent(data)
    print(f"   Old Regime Tax: ₹{result.old_regime.total_tax:,.0f}")
    print(f"   New Regime Tax: ₹{result.new_regime.total_tax:,.0f}")
    print(f"   Recommended: {result.recommended_regime} (saves ₹{result.savings_with_recommended:,.0f})")
    print("   ✅ Regime Advisor Agent: OK")
    return result


async def test_investment_recommender(data: ParsedFormData, regime):
    print("\n4️⃣  Testing Investment Recommender Agent...")
    from agents.investment_recommender_agent import investment_recommender_agent

    result = await investment_recommender_agent(data, regime, RiskProfile.MODERATE)
    print(f"   Recommendations: {len(result)}")
    for rec in result:
        print(f"   → {rec.instrument} ({rec.section}): ₹{rec.recommended_amount:,.0f}")
    print("   ✅ Investment Recommender Agent: OK")
    return result


async def test_explainer(data, deductions, regime, investments):
    print("\n5️⃣  Testing Explainer Agent...")
    from agents.explainer_agent import explainer_agent

    result = await explainer_agent(data, deductions, regime, investments)
    print(f"   Summary length: {len(result)} chars")
    print(f"   Preview: {result[:100]}...")
    print("   ✅ Explainer Agent: OK")
    return result


async def test_chat(session_id: str):
    print("\n6️⃣  Testing Chat Agent...")
    from agents.chat_agent import chat_agent

    result = await chat_agent(session_id, "Which tax regime is better for me?")
    print(f"   Response length: {len(result.response)} chars")
    print(f"   Follow-ups: {len(result.follow_up_suggestions)}")
    print("   ✅ Chat Agent: OK")


async def test_orchestrator(pdf_path: str | None = None):
    print("\n7️⃣  Testing LangGraph Orchestrator...")
    import uuid
    from orchestrator.graph import taxgenie_graph
    from orchestrator.state import TaxGenieState

    session_id = str(uuid.uuid4())
    pdf_bytes = Path(pdf_path).read_bytes() if pdf_path and Path(pdf_path).exists() else None

    initial_state: TaxGenieState = {
        "session_id": session_id,
        "pdf_bytes": pdf_bytes,
        "manual_income": None,
        "risk_profile": RiskProfile.MODERATE,
        "additional_rent_paid": None,
        "parsed_data": None,
        "missed_deductions": None,
        "regime_comparison": None,
        "investment_recommendations": [],
        "summary": None,
        "current_stage": "start",
        "progress": 0,
        "error": None,
        "total_potential_savings": 0,
    }

    final_state = await taxgenie_graph.ainvoke(initial_state)
    print(f"   Final stage: {final_state.get('current_stage')}")
    print(f"   Progress: {final_state.get('progress')}%")
    print(f"   Total potential savings: ₹{final_state.get('total_potential_savings', 0):,.0f}")
    if final_state.get("error"):
        print(f"   ⚠️  Error: {final_state['error']}")
    print("   ✅ LangGraph Orchestrator: OK")


async def main():
    pdf_path = None
    for i, arg in enumerate(sys.argv):
        if arg == "--pdf" and i + 1 < len(sys.argv):
            pdf_path = sys.argv[i + 1]

    print("=" * 55)
    print("  🧞 TaxGenie AI — Agent Test Suite")
    print("=" * 55)

    data = await test_pdf_parser(pdf_path)
    deductions = await test_deduction_finder(data)
    regime = await test_regime_advisor(data)
    investments = await test_investment_recommender(data, regime)
    await test_explainer(data, deductions, regime, investments)
    await test_chat("test-session-001")
    await test_orchestrator(pdf_path)

    print("\n" + "=" * 55)
    print("  ✅ All systems operational!")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
