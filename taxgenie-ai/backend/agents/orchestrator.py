"""
Orchestrator Agent - LangGraph State Machine
Coordinates all specialized agents
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
import operator
from pydantic import BaseModel
from enum import Enum

from agents.pdf_parser_agent import PDFParserAgent
from agents.deduction_agent import DeductionFinderAgent
from agents.regime_agent import RegimeAdvisorAgent
from agents.investment_agent import InvestmentRecommenderAgent
from agents.explainer_agent import ExplainerAgent
from services.llm_gateway import llm


# ============================================
# STATE DEFINITION
# ============================================

class WorkflowStage(str, Enum):
    INIT = "init"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    COMPARING = "comparing"
    RECOMMENDING = "recommending"
    EXPLAINING = "explaining"
    COMPLETE = "complete"
    ERROR = "error"


class AgentState(TypedDict):
    """State passed between agents"""
    # Input
    pdf_content: bytes | None
    manual_input: dict | None
    
    # Extracted data
    tax_data: dict | None
    
    # Analysis results
    missed_deductions: list | None
    regime_comparison: dict | None
    investment_recommendations: list | None
    
    # Final output
    summary: str | None
    explanation: str | None
    
    # Workflow control
    stage: WorkflowStage
    errors: list
    messages: Annotated[Sequence[str], operator.add]


# ============================================
# AGENT NODES
# ============================================

class TaxAnalysisOrchestrator:
    """
    Main orchestrator that coordinates all agents using LangGraph
    """
    
    def __init__(self):
        self.pdf_agent = PDFParserAgent()
        self.deduction_agent = DeductionFinderAgent()
        self.regime_agent = RegimeAdvisorAgent()
        self.investment_agent = InvestmentRecommenderAgent()
        self.explainer_agent = ExplainerAgent()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_pdf", self._parse_pdf_node)
        workflow.add_node("find_deductions", self._find_deductions_node)
        workflow.add_node("compare_regimes", self._compare_regimes_node)
        workflow.add_node("recommend_investments", self._recommend_investments_node)
        workflow.add_node("generate_explanation", self._generate_explanation_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Add edges
        workflow.set_entry_point("parse_pdf")
        
        workflow.add_conditional_edges(
            "parse_pdf",
            self._should_continue_after_parse,
            {
                "continue": "find_deductions",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("find_deductions", "compare_regimes")
        workflow.add_edge("compare_regimes", "recommend_investments")
        workflow.add_edge("recommend_investments", "generate_explanation")
        workflow.add_edge("generate_explanation", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    async def _parse_pdf_node(self, state: AgentState) -> AgentState:
        """Node: Parse PDF and extract tax data"""
        state["stage"] = WorkflowStage.PARSING
        state["messages"] = state.get("messages", []) + ["Starting PDF parsing..."]
        
        try:
            if state.get("pdf_content"):
                tax_data = await self.pdf_agent.parse(state["pdf_content"])
            elif state.get("manual_input"):
                tax_data = state["manual_input"]
            else:
                raise ValueError("No input provided")
            
            state["tax_data"] = tax_data
            state["messages"] = state["messages"] + ["PDF parsed successfully"]
            
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"PDF parsing error: {str(e)}"]
            state["stage"] = WorkflowStage.ERROR
        
        return state
    
    async def _find_deductions_node(self, state: AgentState) -> AgentState:
        """Node: Find missed deductions"""
        state["stage"] = WorkflowStage.ANALYZING
        state["messages"] = state["messages"] + ["Analyzing deductions..."]
        
        try:
            missed = await self.deduction_agent.analyze(state["tax_data"])
            state["missed_deductions"] = missed
            state["messages"] = state["messages"] + [f"Found {len(missed)} saving opportunities"]
            
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Deduction analysis error: {str(e)}"]
        
        return state
    
    async def _compare_regimes_node(self, state: AgentState) -> AgentState:
        """Node: Compare tax regimes"""
        state["stage"] = WorkflowStage.COMPARING
        state["messages"] = state["messages"] + ["Comparing tax regimes..."]
        
        try:
            comparison = await self.regime_agent.compare(state["tax_data"])
            state["regime_comparison"] = comparison
            
            better = comparison.get("recommendation", {}).get("regime", "Unknown")
            savings = comparison.get("comparison", {}).get("savings_amount", 0)
            state["messages"] = state["messages"] + [
                f"Regime analysis complete: {better} saves ₹{savings:,.0f}"
            ]
            
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Regime comparison error: {str(e)}"]
        
        return state
    
    async def _recommend_investments_node(self, state: AgentState) -> AgentState:
        """Node: Recommend investments"""
        state["stage"] = WorkflowStage.RECOMMENDING
        state["messages"] = state["messages"] + ["Generating investment recommendations..."]
        
        try:
            recommendations = await self.investment_agent.recommend(
                state["tax_data"],
                state["missed_deductions"]
            )
            state["investment_recommendations"] = recommendations
            state["messages"] = state["messages"] + ["Investment recommendations ready"]
            
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Investment recommendation error: {str(e)}"]
        
        return state
    
    async def _generate_explanation_node(self, state: AgentState) -> AgentState:
        """Node: Generate plain-English explanation"""
        state["stage"] = WorkflowStage.EXPLAINING
        state["messages"] = state["messages"] + ["Generating personalized explanation..."]
        
        try:
            explanation = await self.explainer_agent.explain(
                tax_data=state["tax_data"],
                missed_deductions=state["missed_deductions"],
                regime_comparison=state["regime_comparison"],
                investments=state["investment_recommendations"]
            )
            state["explanation"] = explanation
            state["summary"] = explanation  # Use as summary too
            state["stage"] = WorkflowStage.COMPLETE
            state["messages"] = state["messages"] + ["Analysis complete!"]
            
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Explanation generation error: {str(e)}"]
        
        return state
    
    async def _handle_error_node(self, state: AgentState) -> AgentState:
        """Node: Handle errors gracefully"""
        state["stage"] = WorkflowStage.ERROR
        error_summary = "; ".join(state.get("errors", ["Unknown error"]))
        state["explanation"] = f"Analysis encountered errors: {error_summary}. Please try again or enter data manually."
        return state
    
    def _should_continue_after_parse(self, state: AgentState) -> Literal["continue", "error"]:
        """Conditional edge: Check if parsing was successful"""
        if state.get("tax_data") and state["stage"] != WorkflowStage.ERROR:
            return "continue"
        return "error"
    
    async def run(
        self,
        pdf_content: bytes = None,
        manual_input: dict = None
    ) -> dict:
        """
        Run the complete tax analysis workflow
        """
        initial_state: AgentState = {
            "pdf_content": pdf_content,
            "manual_input": manual_input,
            "tax_data": None,
            "missed_deductions": None,
            "regime_comparison": None,
            "investment_recommendations": None,
            "summary": None,
            "explanation": None,
            "stage": WorkflowStage.INIT,
            "errors": [],
            "messages": ["Starting TaxGenie analysis..."]
        }
        
        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "success": final_state["stage"] == WorkflowStage.COMPLETE,
            "tax_data": final_state.get("tax_data"),
            "missed_deductions": final_state.get("missed_deductions"),
            "regime_comparison": final_state.get("regime_comparison"),
            "investment_recommendations": final_state.get("investment_recommendations"),
            "summary": final_state.get("summary"),
            "explanation": final_state.get("explanation"),
            "errors": final_state.get("errors", []),
            "workflow_messages": final_state.get("messages", [])
        }


# Create singleton
orchestrator = TaxAnalysisOrchestrator()