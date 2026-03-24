"""
TaxGenie AI - LangGraph Nodes
Each function is one node in the state machine graph.
"""

import logging
from orchestrator.state import TaxGenieState
from agents.pdf_parser_agent import parse_pdf_agent
from agents.deduction_finder_agent import find_deductions_agent
from agents.regime_advisor_agent import regime_advisor_agent
from agents.investment_recommender_agent import investment_recommender_agent
from agents.explainer_agent import explainer_agent
from services.memory_store import save_session

logger = logging.getLogger(__name__)


async def parse_pdf_node(state: TaxGenieState) -> TaxGenieState:
    """Node 1: Parse the uploaded PDF using GPT-4o + PyMuPDF."""
    logger.info(f"[{state['session_id']}] Stage: parse_pdf")
    state["current_stage"] = "parsing"
    state["progress"] = 10

    try:
        pdf_bytes = state.get("pdf_bytes")
        manual_income = state.get("manual_income")

        if pdf_bytes:
            parsed = await parse_pdf_agent(pdf_bytes)
            # Override gross salary if manual income provided
            if manual_income and manual_income > 0:
                parsed.gross_salary = manual_income
        elif manual_income:
            # No PDF — create minimal data from manual input
            from models.response_models import ParsedFormData, Section80CBreakdown, Section80DBreakdown
            parsed = ParsedFormData(
                gross_salary=manual_income,
                basic_salary=manual_income * 0.5,
                standard_deduction=50_000,
                section_80c_investments=Section80CBreakdown(),
                section_80d_premium=Section80DBreakdown(),
                assessment_year="2025-26",
            )
        else:
            raise ValueError("No PDF or manual income provided")

        state["parsed_data"] = parsed
        state["progress"] = 25

    except Exception as e:
        logger.error(f"parse_pdf_node failed: {e}")
        state["error"] = f"PDF parsing failed: {str(e)}"

    return state


async def find_deductions_node(state: TaxGenieState) -> TaxGenieState:
    """Node 2: Find missed deductions using Claude + RAG."""
    logger.info(f"[{state['session_id']}] Stage: find_deductions")
    state["current_stage"] = "analyzing"
    state["progress"] = 35

    if state.get("error") or not state.get("parsed_data"):
        return state

    try:
        deductions = await find_deductions_agent(state["parsed_data"])
        state["missed_deductions"] = deductions
        state["progress"] = 55

    except Exception as e:
        logger.error(f"find_deductions_node failed: {e}")
        state["error"] = f"Deduction analysis failed: {str(e)}"

    return state


async def compare_regimes_node(state: TaxGenieState) -> TaxGenieState:
    """Node 3: Compare Old vs New Regime with exact math."""
    logger.info(f"[{state['session_id']}] Stage: compare_regimes")
    state["current_stage"] = "calculating"
    state["progress"] = 60

    if state.get("error") or not state.get("parsed_data"):
        return state

    try:
        comparison = await regime_advisor_agent(state["parsed_data"])
        state["regime_comparison"] = comparison
        state["progress"] = 72

    except Exception as e:
        logger.error(f"compare_regimes_node failed: {e}")
        state["error"] = f"Regime comparison failed: {str(e)}"

    return state


async def recommend_investments_node(state: TaxGenieState) -> TaxGenieState:
    """Node 4: Generate personalised investment recommendations."""
    logger.info(f"[{state['session_id']}] Stage: recommend_investments")
    state["current_stage"] = "recommending"
    state["progress"] = 78

    if state.get("error") or not state.get("parsed_data") or not state.get("regime_comparison"):
        return state

    try:
        recommendations = await investment_recommender_agent(
            data=state["parsed_data"],
            regime=state["regime_comparison"],
            risk_profile=state.get("risk_profile", "moderate"),
        )
        state["investment_recommendations"] = recommendations
        state["progress"] = 88

    except Exception as e:
        logger.error(f"recommend_investments_node failed: {e}")
        state["investment_recommendations"] = []

    return state


async def generate_report_node(state: TaxGenieState) -> TaxGenieState:
    """Node 5: Generate plain-English summary report using Claude."""
    logger.info(f"[{state['session_id']}] Stage: generate_report")
    state["current_stage"] = "done"
    state["progress"] = 93

    if not state.get("parsed_data"):
        state["summary"] = "Analysis could not be completed. Please try uploading again."
        state["progress"] = 100
        return state

    try:
        summary = await explainer_agent(
            parsed_data=state["parsed_data"],
            deductions=state.get("missed_deductions"),
            regime=state.get("regime_comparison"),
            investments=state.get("investment_recommendations", []),
        )
        state["summary"] = summary

        # Calculate total potential savings
        regime_savings = state["regime_comparison"].savings_with_recommended if state.get("regime_comparison") else 0
        deduction_savings = state["missed_deductions"].total_potential_savings if state.get("missed_deductions") else 0
        state["total_potential_savings"] = regime_savings + deduction_savings

    except Exception as e:
        logger.error(f"generate_report_node failed: {e}")
        state["summary"] = "Your tax analysis is ready. Review the results above for details."

    # Persist final result to memory store
    _persist_session(state)
    state["progress"] = 100

    return state


def _persist_session(state: TaxGenieState) -> None:
    """Save the completed analysis to Redis/memory."""
    try:
        data = {
            "session_id": state["session_id"],
            "status": "completed",
            "parsed_data": state["parsed_data"].model_dump() if state.get("parsed_data") else None,
            "missed_deductions": state["missed_deductions"].model_dump() if state.get("missed_deductions") else None,
            "regime_comparison": state["regime_comparison"].model_dump() if state.get("regime_comparison") else None,
            "investment_recommendations": [r.model_dump() for r in state.get("investment_recommendations", [])],
            "summary": state.get("summary"),
            "total_potential_savings": state.get("total_potential_savings", 0),
            "error": state.get("error"),
        }
        save_session(state["session_id"], data)
    except Exception as e:
        logger.error(f"Session persistence failed: {e}")
