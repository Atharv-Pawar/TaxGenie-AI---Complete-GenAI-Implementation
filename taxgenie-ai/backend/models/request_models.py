"""
TaxGenie AI - Pydantic Request Models
Validates all incoming API request bodies.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class RiskProfileEnum(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE     = "moderate"
    AGGRESSIVE   = "aggressive"


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadRequest(BaseModel):
    """
    Metadata sent alongside a PDF upload.
    The actual file comes as multipart/form-data — this model
    validates the optional form fields.
    """
    risk_profile: RiskProfileEnum = Field(
        RiskProfileEnum.MODERATE,
        description="Investment risk tolerance of the user"
    )
    additional_rent_paid: Optional[float] = Field(
        None,
        ge=0,
        description="Monthly rent paid by the user (for HRA calculation)"
    )


# ── Analysis ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """
    Request body for POST /api/v1/analyze and /api/v1/analyze/sync.
    Sent as multipart/form-data so all fields are strings from the form.
    """
    session_id: str = Field(
        ...,
        description="Session ID returned by the /upload endpoint"
    )
    risk_profile: RiskProfileEnum = Field(
        RiskProfileEnum.MODERATE,
        description="Investment risk tolerance"
    )
    manual_income: Optional[float] = Field(
        None,
        ge=0,
        description="Override gross salary if PDF parsing fails or no PDF uploaded"
    )
    additional_rent_paid: Optional[float] = Field(
        None,
        ge=0,
        description="Monthly rent paid — used to calculate HRA exemption"
    )

    @validator("session_id")
    def session_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("session_id cannot be empty")
        return v.strip()


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    Request body for POST /api/v1/chat.
    """
    session_id: str = Field(
        ...,
        description="Session ID — used to load tax analysis context"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question or message to TaxGenie"
    )
    context_type: str = Field(
        "tax_analysis",
        description="Type of context to load — always tax_analysis for now"
    )

    @validator("message")
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()


# ── Manual Income ─────────────────────────────────────────────────────────────

class ManualIncomeRequest(BaseModel):
    """
    For users who want to enter income manually without uploading a PDF.
    """
    gross_salary: float = Field(
        ...,
        gt=0,
        description="Annual gross salary in rupees"
    )
    basic_salary: Optional[float] = Field(
        None,
        ge=0,
        description="Basic salary component — defaults to 50% of gross if not provided"
    )
    hra_received: Optional[float] = Field(
        None,
        ge=0,
        description="Annual HRA received from employer"
    )
    pf_contribution: Optional[float] = Field(
        None,
        ge=0,
        description="Annual PF contribution"
    )
    risk_profile: RiskProfileEnum = Field(
        RiskProfileEnum.MODERATE,
        description="Investment risk tolerance"
    )

    @validator("basic_salary", always=True)
    def default_basic_salary(cls, v, values):
        if v is None and "gross_salary" in values:
            return values["gross_salary"] * 0.5
        return v
