# agents/orchestrator.py
"""
Orchestrator Agent
Uses LangGraph StateGraph to coordinate all specialized agents
in a structured, auditable multi-agent pipeline.
"""

import logging
from typing import TypedDict, Annotated, Sequence, Literal, Optional
import operator

from langgraph.graph import StateGraph, END

from agents.pdf_parser_agent import PDFParserAgent
from agents.deduction_agent import DeductionFinderAgent
from agents.regime_agent import RegimeAdvisorAgent
from agents.investment_agent import InvestmentRecommenderAgent
from agents.explainer_agent import ExplainerAgent

logger = logging.getLogger(__name__)


# ============================================================
# STATE DEFINITION
# ============================================================

class AgentState(TypedDict):
    """
    Shared state passed between all agents in the LangGraph pipeline.
    Each agent reads from and writes to this state.
    """
    # ── Inputs ──
    pdf_content:      Optional[bytes]
    manual_input:     Optional[dict]

    # ── Intermediate Results ──
    tax_data:                    Optional[dict]
    missed_deductions:           Optional[list]
    regime_comparison:           Optional[dict]
    investment_recommendations:  Optional[list]

    # ── Final Output ──
    explanation: Optional[str]
    summary:     Optional[str]

    # ── Workflow Control ──
    stage:    str
    errors:   list
    messages: Annotated[Sequence[str], operator.add]


# ============================================================
# ORCHESTRATOR CLASS
# ============================================================

class TaxAnalysisOrchestrator:
    """
    Multi-agent orchestrator that coordinates all tax analysis agents.

    Pipeline:
        Input (PDF / Manual)
            ↓
        PDFParserAgent      → Extracts structured tax data
            ↓
        DeductionFinderAgent → Finds missed deductions
            ↓
        RegimeAdvisorAgent   → Compares Old vs New regime
            ↓
        InvestmentAgent      → Recommends investments
            ↓
        ExplainerAgent       → Generates plain-English summary
            ↓
        Final Response
    """

    def __init__(self):
        # Initialize all specialized agents
        self.pdf_agent        = PDFParserAgent()
        self.deduction_agent  = DeductionFinderAgent()
        self.regime_agent     = RegimeAdvisorAgent()
        self.investment_agent = InvestmentRecommenderAgent()
        self.explainer_agent  = ExplainerAgent()

        # Build the LangGraph workflow
        self.graph = self._build_graph()

    # ────────────────────────────────────────────────────────
    # GRAPH CONSTRUCTION
    # ────────────────────────────────────────────────────────

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        Each node is a specialized agent.
        Edges define the flow between agents.
        """
        graph = StateGraph(AgentState)

        # ── Register Nodes ──
        graph.add_node("parse_input",          self._parse_input_node)
        graph.add_node("find_deductions",      self._find_deductions_node)
        graph.add_node("compare_regimes",      self._compare_regimes_node)
        graph.add_node("recommend_investments",self._recommend_investments_node)
        graph.add_node("generate_explanation", self._generate_explanation_node)
        graph.add_node("handle_error",         self._handle_error_node)

        # ── Entry Point ──
        graph.set_entry_point("parse_input")

        # ── Conditional Edge after parsing ──
        graph.add_conditional_edges(
            "parse_input",
            self._check_parse_success,
            {
                "success": "find_deductions",
                "error":   "handle_error",
            }
        )

        # ── Sequential Edges ──
        graph.add_edge("find_deductions",       "compare_regimes")
        graph.add_edge("compare_regimes",       "recommend_investments")
        graph.add_edge("recommend_investments", "generate_explanation")
        graph.add_edge("generate_explanation",  END)
        graph.add_edge("handle_error",          END)

        return graph.compile()

    # ────────────────────────────────────────────────────────
    # NODE IMPLEMENTATIONS
    # ────────────────────────────────────────────────────────

    async def _parse_input_node(self, state: AgentState) -> dict:
        """
        Node 1: Parse PDF or accept manual input.
        Uses GPT-4 Vision for image-based extraction.
        """
        logger.info("[Orchestrator] Stage: Parsing input")

        try:
            if state.get("pdf_content"):
                tax_data = await self.pdf_agent.parse(state["pdf_content"])
            elif state.get("manual_input"):
                tax_data = state["manual_input"]
            else:
                raise ValueError("No input provided — attach PDF or fill manual form")

            if not tax_data or tax_data.get("gross_salary", 0) == 0:
                raise ValueError("Could not extract valid data from document")

            return {
                "tax_data": tax_data,
                "stage":    "parsed",
                "messages": ["✅ Input parsed successfully"],
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Parse error: {e}")
            return {
                "stage":    "error",
                "errors":   [f"Parse failed: {str(e)}"],
                "messages": [f"❌ Parse failed: {str(e)}"],
            }

    async def _find_deductions_node(self, state: AgentState) -> dict:
        """
        Node 2: Find all missed tax deductions.
        Uses Claude / GPT-4 with RAG tax knowledge base.
        """
        logger.info("[Orchestrator] Stage: Finding deductions")

        try:
            missed = await self.deduction_agent.analyze(state["tax_data"])
            total  = sum(d.get("potential_tax_saving", 0) for d in missed)

            return {
                "missed_deductions": missed,
                "stage":    "deductions_found",
                "messages": [
                    f"✅ Found {len(missed)} saving opportunities "
                    f"(Total: ₹{total:,.0f})"
                ],
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Deduction error: {e}")
            return {
                "missed_deductions": [],
                "errors":   state.get("errors", []) + [f"Deduction analysis: {e}"],
                "messages": [f"⚠️ Deduction analysis had issues: {e}"],
            }

    async def _compare_regimes_node(self, state: AgentState) -> dict:
        """
        Node 3: Compare Old vs New tax regime.
        Uses GPT-4 for calculations + recommendations.
        """
        logger.info("[Orchestrator] Stage: Comparing regimes")

        try:
            comparison = await self.regime_agent.compare(state["tax_data"])
            better     = comparison.get("comparison", {}).get("better_regime", "N/A")
            savings    = comparison.get("comparison", {}).get("savings_amount", 0)

            return {
                "regime_comparison": comparison,
                "stage":    "regimes_compared",
                "messages": [
                    f"✅ Regime comparison done: "
                    f"{better} regime saves ₹{savings:,.0f}"
                ],
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Regime error: {e}")
            return {
                "regime_comparison": {},
                "errors":   state.get("errors", []) + [f"Regime comparison: {e}"],
                "messages": [f"⚠️ Regime comparison had issues: {e}"],
            }

    async def _recommend_investments_node(self, state: AgentState) -> dict:
        """
        Node 4: Recommend tax-saving investments.
        Uses GPT-4 with user risk profile + missed deductions.
        """
        logger.info("[Orchestrator] Stage: Recommending investments")

        try:
            recommendations = await self.investment_agent.recommend(
                tax_data          = state["tax_data"],
                missed_deductions = state.get("missed_deductions", [])
            )

            return {
                "investment_recommendations": recommendations,
                "stage":    "investments_recommended",
                "messages": [
                    f"✅ {len(recommendations)} investment recommendations generated"
                ],
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Investment error: {e}")
            return {
                "investment_recommendations": [],
                "errors":   state.get("errors", []) + [f"Investment rec: {e}"],
                "messages": [f"⚠️ Investment recommendations had issues: {e}"],
            }

    async def _generate_explanation_node(self, state: AgentState) -> dict:
        """
        Node 5: Generate plain-English explanation.
        Uses Claude for natural, helpful language.
        """
        logger.info("[Orchestrator] Stage: Generating explanation")

        try:
            explanation = await self.explainer_agent.explain(
                tax_data         = state["tax_data"],
                missed_deductions= state.get("missed_deductions", []),
                regime_comparison= state.get("regime_comparison", {}),
                investments      = state.get("investment_recommendations", [])
            )

            return {
                "explanation": explanation,
                "summary":     explanation,
                "stage":       "complete",
                "messages":    ["✅ Analysis complete!"],
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Explainer error: {e}")
            return {
                "explanation": "Analysis complete. Please review the sections below.",
                "summary":     "Analysis complete.",
                "stage":       "complete",
                "messages":    [f"⚠️ Summary generation had issues: {e}"],
            }

    async def _handle_error_node(self, state: AgentState) -> dict:
        """
        Error node: Called when pipeline fails.
        Returns a graceful degraded response.
        """
        logger.warning("[Orchestrator] Entering error handler")
        errors = state.get("errors", ["Unknown error"])

        return {
            "explanation": (
                "We encountered issues processing your document. "
                "Please try again or enter your tax data manually."
            ),
            "summary": "Processing failed — please try manual entry.",
            "stage":   "error",
            "messages": [f"❌ Errors: {'; '.join(str(e) for e in errors)}"],
        }

    # ────────────────────────────────────────────────────────
    # CONDITIONAL EDGE FUNCTION
    # ────────────────────────────────────────────────────────

    def _check_parse_success(
        self,
        state: AgentState
    ) -> Literal["success", "error"]:
        """
        Decide whether to continue pipeline or route to error handler.
        """
        if state.get("tax_data") and state.get("stage") != "error":
            return "success"
        return "error"

    # ────────────────────────────────────────────────────────
    # PUBLIC RUN METHOD
    # ────────────────────────────────────────────────────────

    async def run(
        self,
        pdf_content:  Optional[bytes] = None,
        manual_input: Optional[dict]  = None
    ) -> dict:
        """
        Run the complete multi-agent tax analysis pipeline.

        Args:
            pdf_content:  Raw bytes of Form 16 PDF
            manual_input: Dict of manually entered tax values

        Returns:
            Complete analysis result dict
        """
        # Build initial state
        initial_state: AgentState = {
            "pdf_content":               pdf_content,
            "manual_input":              manual_input,
            "tax_data":                  None,
            "missed_deductions":         None,
            "regime_comparison":         None,
            "investment_recommendations":None,
            "explanation":               None,
            "summary":                   None,
            "stage":                     "init",
            "errors":                    [],
            "messages":                  ["🚀 TaxGenie analysis started..."],
        }

        logger.info("[Orchestrator] Starting pipeline")

        # Execute the graph
        final_state = await self.graph.ainvoke(initial_state)

        logger.info(f"[Orchestrator] Pipeline finished: stage={final_state.get('stage')}")

        # Return clean response
        return {
            "success":                   final_state.get("stage") == "complete",
            "tax_data":                  final_state.get("tax_data"),
            "missed_deductions":         final_state.get("missed_deductions", []),
            "regime_comparison":         final_state.get("regime_comparison", {}),
            "investment_recommendations":final_state.get("investment_recommendations", []),
            "explanation":               final_state.get("explanation", ""),
            "summary":                   final_state.get("summary", ""),
            "errors":                    final_state.get("errors", []),
            "workflow_log":              list(final_state.get("messages", [])),
        }


# ── Singleton ──
orchestrator = TaxAnalysisOrchestrator()