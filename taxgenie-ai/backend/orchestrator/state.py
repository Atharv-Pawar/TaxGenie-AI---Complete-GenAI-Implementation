"""
TaxGenie AI - LangGraph State
Defines the shared state object that flows through all graph nodes.
"""

from typing import TypedDict, Optional, List
from models.response_models import (
    ParsedFormData,
    DeductionResult,
    RegimeComparison,
    InvestmentRecommendation,
    RiskProfile,
)


class TaxGenieState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    Each node reads what it needs and writes its output back to state.
    """
    # Inputs
    session_id: str
    pdf_bytes: Optional[bytes]
    manual_income: Optional[float]
    risk_profile: RiskProfile
    additional_rent_paid: Optional[float]

    # Stage outputs (populated by each node)
    parsed_data: Optional[ParsedFormData]
    missed_deductions: Optional[DeductionResult]
    regime_comparison: Optional[RegimeComparison]
    investment_recommendations: List[InvestmentRecommendation]
    summary: Optional[str]

    # Control
    current_stage: str          # "parsing" | "analyzing" | "calculating" | "recommending" | "done"
    progress: int               # 0-100
    error: Optional[str]
    total_potential_savings: float
