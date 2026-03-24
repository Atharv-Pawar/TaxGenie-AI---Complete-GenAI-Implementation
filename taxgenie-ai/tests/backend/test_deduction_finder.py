"""
Tests for Deduction Finder Agent
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from models.response_models import ParsedFormData, Section80CBreakdown, Section80DBreakdown


def make_test_data(**kwargs) -> ParsedFormData:
    defaults = dict(
        gross_salary=1_200_000,
        basic_salary=600_000,
        hra_received=240_000,
        standard_deduction=50_000,
        professional_tax=2_400,
        section_80c_investments=Section80CBreakdown(pf=72_000, lic_premium=15_000, total=87_000),
        section_80d_premium=Section80DBreakdown(self_family=12_000, total=12_000),
        assessment_year="2025-26",
    )
    defaults.update(kwargs)
    return ParsedFormData(**defaults)


@pytest.mark.asyncio
async def test_finds_80c_gap():
    from agents.deduction_finder_agent import _rule_based_deductions

    data = make_test_data()  # 80C = 87,000 → gap = 63,000
    result = _rule_based_deductions(data)

    sections = [d.section for d in result.missed_deductions]
    assert "80C" in sections


@pytest.mark.asyncio
async def test_no_80c_gap_when_maxed():
    from agents.deduction_finder_agent import _rule_based_deductions

    data = make_test_data(
        section_80c_investments=Section80CBreakdown(pf=150_000, total=150_000)
    )
    result = _rule_based_deductions(data)

    sections = [d.section for d in result.missed_deductions]
    assert "80C" not in sections


@pytest.mark.asyncio
async def test_nps_suggested_when_missing():
    from agents.deduction_finder_agent import _rule_based_deductions

    data = make_test_data()  # nps_contribution defaults to 0
    result = _rule_based_deductions(data)

    sections = [d.section for d in result.missed_deductions]
    assert any("NPS" in s or "80CCD" in s for s in sections)


@pytest.mark.asyncio
async def test_total_potential_savings_positive():
    from agents.deduction_finder_agent import _rule_based_deductions

    data = make_test_data()
    result = _rule_based_deductions(data)

    assert result.total_potential_savings > 0


@pytest.mark.asyncio
async def test_full_agent_returns_deduction_result():
    from agents.deduction_finder_agent import find_deductions_agent
    from models.response_models import DeductionResult

    data = make_test_data()
    result = await find_deductions_agent(data)

    assert isinstance(result, DeductionResult)
    assert result.total_potential_savings >= 0
