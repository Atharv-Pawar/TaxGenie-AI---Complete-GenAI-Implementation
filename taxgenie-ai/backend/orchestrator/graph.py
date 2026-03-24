"""
TaxGenie AI - LangGraph State Machine
Defines the main orchestration graph that connects all AI agents.
"""

from langgraph.graph import StateGraph, END
from orchestrator.state import TaxGenieState
from orchestrator.nodes import (
    parse_pdf_node,
    find_deductions_node,
    compare_regimes_node,
    recommend_investments_node,
    generate_report_node,
)


def create_taxgenie_graph() -> StateGraph:
    """
    Creates and returns the compiled TaxGenie LangGraph state machine.

    Flow:
      parse_pdf → find_deductions → compare_regimes → recommend_investments → generate_report → END
    """
    workflow = StateGraph(TaxGenieState)

    # Register all nodes
    workflow.add_node("parse_pdf", parse_pdf_node)
    workflow.add_node("find_deductions", find_deductions_node)
    workflow.add_node("compare_regimes", compare_regimes_node)
    workflow.add_node("recommend_investments", recommend_investments_node)
    workflow.add_node("generate_report", generate_report_node)

    # Define the linear pipeline
    workflow.set_entry_point("parse_pdf")
    workflow.add_edge("parse_pdf", "find_deductions")
    workflow.add_edge("find_deductions", "compare_regimes")
    workflow.add_edge("compare_regimes", "recommend_investments")
    workflow.add_edge("recommend_investments", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()


# Singleton compiled graph — import this in your API handlers
taxgenie_graph = create_taxgenie_graph()
