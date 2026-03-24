"""
Tests for LangGraph Orchestrator
"""
import pytest
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from models.response_models import RiskProfile


@pytest.mark.asyncio
async def test_orchestrator_full_pipeline():
    from orchestrator.graph import taxgenie_graph
    from orchestrator.state import TaxGenieState

    session_id = str(uuid.uuid4())

    initial_state: TaxGenieState = {
        "session_id": session_id,
        "pdf_bytes": None,
        "manual_income": 1_000_000,
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

    assert final_state["progress"] == 100
    assert final_state["current_stage"] == "done"
    assert final_state["parsed_data"] is not None
    assert final_state["regime_comparison"] is not None
    assert final_state["summary"] is not None


@pytest.mark.asyncio
async def test_orchestrator_session_persisted():
    from orchestrator.graph import taxgenie_graph
    from orchestrator.state import TaxGenieState
    from services.memory_store import get_session

    session_id = str(uuid.uuid4())

    initial_state: TaxGenieState = {
        "session_id": session_id,
        "pdf_bytes": None,
        "manual_income": 800_000,
        "risk_profile": RiskProfile.CONSERVATIVE,
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

    await taxgenie_graph.ainvoke(initial_state)

    stored = get_session(session_id)
    assert stored is not None
    assert stored.get("status") == "completed"


@pytest.mark.asyncio
async def test_orchestrator_with_zero_income_no_crash():
    from orchestrator.graph import taxgenie_graph
    from orchestrator.state import TaxGenieState

    session_id = str(uuid.uuid4())

    initial_state: TaxGenieState = {
        "session_id": session_id,
        "pdf_bytes": None,
        "manual_income": None,  # No income, no PDF
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

    # Should not raise, error captured in state
    final_state = await taxgenie_graph.ainvoke(initial_state)
    assert final_state is not None
