"""
Tests for PDF Parser Agent
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from models.response_models import ParsedFormData


@pytest.mark.asyncio
async def test_pdf_parser_returns_parsed_form_data():
    from agents.pdf_parser_agent import parse_pdf_agent, _demo_form_data

    # With dummy bytes (no valid PDF), should fall back to demo data
    result = await parse_pdf_agent(b"not a real pdf")
    assert isinstance(result, ParsedFormData)
    assert result.gross_salary > 0
    assert result.assessment_year is not None


@pytest.mark.asyncio
async def test_demo_form_data_values():
    from agents.pdf_parser_agent import _demo_form_data

    data = _demo_form_data()
    assert data.gross_salary == 1_200_000
    assert data.basic_salary == 600_000
    assert data.section_80c_investments.total == 87_000
    assert data.section_80d_premium.total == 12_000
    assert data.employer_name == "Tech Corp Pvt Ltd"


def test_dict_to_parsed_form():
    from agents.pdf_parser_agent import _dict_to_parsed_form

    raw = {
        "gross_salary": 800000,
        "basic_salary": 400000,
        "hra_received": 160000,
        "standard_deduction": 50000,
        "professional_tax": 2400,
        "section_80c_investments": {"pf": 48000, "lic_premium": 12000, "total": 60000},
        "section_80d_premium": {"self_family": 15000, "total": 15000},
        "total_tds_deducted": 45000,
        "assessment_year": "2025-26",
    }
    result = _dict_to_parsed_form(raw)
    assert result.gross_salary == 800_000
    assert result.section_80c_investments.pf == 48_000
    assert result.section_80d_premium.self_family == 15_000
