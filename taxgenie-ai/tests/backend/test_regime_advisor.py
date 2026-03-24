"""
Tests for Regime Advisor Agent and Tax Calculator
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from models.response_models import ParsedFormData, Section80CBreakdown, Section80DBreakdown
from services.tax_calculator import (
    calculate_old_regime_tax,
    calculate_new_regime_tax,
    apply_rebate_87a,
    add_cess,
    compare_regimes,
)


# ─── Pure Math Tests ──────────────────────────────────────────────────────────

def test_old_regime_zero_tax_below_slab():
    assert calculate_old_regime_tax(200_000) == 0


def test_old_regime_5_percent_slab():
    tax = calculate_old_regime_tax(400_000)
    assert tax == (400_000 - 250_000) * 0.05  # = 7500


def test_old_regime_20_percent_slab():
    tax = calculate_old_regime_tax(800_000)
    expected = 12_500 + (800_000 - 500_000) * 0.20  # = 72500
    assert tax == expected


def test_old_regime_30_percent_slab():
    tax = calculate_old_regime_tax(1_500_000)
    expected = 112_500 + (1_500_000 - 1_000_000) * 0.30  # = 262500
    assert tax == expected


def test_new_regime_zero_below_3l():
    assert calculate_new_regime_tax(250_000) == 0


def test_new_regime_5_percent_slab():
    tax = calculate_new_regime_tax(500_000)
    expected = (500_000 - 300_000) * 0.05  # = 10000
    assert tax == expected


def test_rebate_87a_old_regime():
    # Income <= 5L: rebate applies
    tax = calculate_old_regime_tax(490_000)  # = 12000
    after = apply_rebate_87a(tax, 490_000, "old")
    assert after == max(0, tax - 12_500)


def test_rebate_87a_no_rebate_above_5l():
    tax = calculate_old_regime_tax(600_000)
    after = apply_rebate_87a(tax, 600_000, "old")
    assert after == tax  # No rebate


def test_cess_calculation():
    total, cess = add_cess(100_000)
    assert cess == 4_000
    assert total == 104_000


# ─── Integration Tests ────────────────────────────────────────────────────────

def make_priya_data() -> ParsedFormData:
    """Priya: ₹12 LPA software developer from README."""
    return ParsedFormData(
        gross_salary=1_200_000,
        basic_salary=600_000,
        hra_received=240_000,
        standard_deduction=50_000,
        professional_tax=2_400,
        section_80c_investments=Section80CBreakdown(pf=72_000, lic_premium=15_000, total=87_000),
        section_80d_premium=Section80DBreakdown(self_family=12_000, total=12_000),
        assessment_year="2025-26",
    )


def test_compare_regimes_returns_comparison():
    data = make_priya_data()
    result = compare_regimes(data)

    assert result.old_regime.total_tax > 0
    assert result.new_regime.total_tax > 0
    assert result.recommended_regime in ("OLD", "NEW")
    assert result.savings_with_recommended >= 0


def test_priya_new_regime_is_recommended():
    """For Priya with ₹87K in 80C, New Regime should save more."""
    data = make_priya_data()
    result = compare_regimes(data)

    # New regime should be recommended given low deductions
    assert result.recommended_regime == "NEW"
    assert result.new_regime.total_tax < result.old_regime.total_tax


def test_old_regime_recommended_with_max_deductions():
    """With full deductions, Old Regime should win."""
    data = ParsedFormData(
        gross_salary=1_200_000,
        basic_salary=600_000,
        standard_deduction=50_000,
        professional_tax=2_400,
        section_80c_investments=Section80CBreakdown(pf=150_000, total=150_000),
        section_80d_premium=Section80DBreakdown(self_family=25_000, parents=25_000, total=50_000),
        nps_contribution=50_000,
        home_loan_interest=200_000,
        assessment_year="2025-26",
    )
    result = compare_regimes(data)
    assert result.recommended_regime == "OLD"


@pytest.mark.asyncio
async def test_regime_advisor_agent():
    from agents.regime_advisor_agent import regime_advisor_agent

    data = make_priya_data()
    result = await regime_advisor_agent(data)

    assert result.recommended_regime in ("OLD", "NEW")
    assert result.recommendation_reason
    assert len(result.recommendation_reason) > 10
