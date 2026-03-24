"""
TaxGenie AI - Pydantic Models
Request and response models for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


# ─── Request Models ───────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    manual_income: Optional[float] = Field(None, description="Manual income override if PDF parsing fails")
    risk_profile: RiskProfile = Field(RiskProfile.MODERATE, description="Investment risk tolerance")
    additional_rent_paid: Optional[float] = Field(None, description="Monthly rent paid (for HRA calculation)")


class ChatRequest(BaseModel):
    session_id: str
    message: str
    context_type: str = "tax_analysis"


# ─── Response Models ──────────────────────────────────────────────────────────

class Section80CBreakdown(BaseModel):
    pf: float = 0
    ppf: float = 0
    elss: float = 0
    lic_premium: float = 0
    nsc: float = 0
    home_loan_principal: float = 0
    tuition_fees: float = 0
    total: float = 0


class Section80DBreakdown(BaseModel):
    self_family: float = 0
    parents: float = 0
    total: float = 0


class ParsedFormData(BaseModel):
    gross_salary: float = 0
    basic_salary: float = 0
    hra_received: float = 0
    lta: float = 0
    special_allowance: float = 0
    standard_deduction: float = 50000
    professional_tax: float = 0
    section_80c_investments: Section80CBreakdown = Field(default_factory=Section80CBreakdown)
    section_80d_premium: Section80DBreakdown = Field(default_factory=Section80DBreakdown)
    home_loan_interest: float = 0
    education_loan_interest: float = 0
    total_tds_deducted: float = 0
    employer_name: Optional[str] = None
    pan_number: Optional[str] = None
    assessment_year: str = "2025-26"
    nps_contribution: float = 0


class MissedDeduction(BaseModel):
    section: str
    potential_saving: float
    description: str
    suggestions: List[str]
    urgency: Literal["HIGH", "MEDIUM", "LOW"]


class DeductionResult(BaseModel):
    claimed_deductions: List[dict] = []
    missed_deductions: List[MissedDeduction] = []
    total_potential_savings: float = 0


class RegimeBreakdown(BaseModel):
    gross_income: float
    total_deductions: float = 0
    taxable_income: float
    tax_before_cess: float
    health_education_cess: float
    total_tax: float
    breakdown: dict = {}


class RegimeComparison(BaseModel):
    old_regime: RegimeBreakdown
    new_regime: RegimeBreakdown
    recommended_regime: Literal["OLD", "NEW"]
    savings_with_recommended: float
    recommendation_reason: str
    breakeven_deduction_amount: float


class InvestmentRecommendation(BaseModel):
    instrument: str
    section: str
    recommended_amount: float
    expected_returns: str
    lock_in_period: str
    risk_level: str
    reason: str
    top_picks: List[str] = []


class AnalysisResult(BaseModel):
    session_id: str
    status: Literal["processing", "completed", "failed"] = "processing"
    parsed_data: Optional[ParsedFormData] = None
    missed_deductions: Optional[DeductionResult] = None
    regime_comparison: Optional[RegimeComparison] = None
    investment_recommendations: List[InvestmentRecommendation] = []
    summary: Optional[str] = None
    total_potential_savings: float = 0
    error: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    follow_up_suggestions: List[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    services: dict = {}
