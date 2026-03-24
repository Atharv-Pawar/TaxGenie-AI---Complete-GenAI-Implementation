"""
TaxGenie AI - PDF Parser Agent
Uses GPT-4o to extract structured financial data from Form 16 PDFs.
"""

import json
import logging
from services.llm_gateway import llm_call
from services.pdf_extractor import extract_text_from_bytes
from models.response_models import ParsedFormData, Section80CBreakdown, Section80DBreakdown
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert Indian tax document parser specialising in Form 16, Form 26AS, and salary slips.
Extract ALL financial information from the provided document text and return ONLY a valid JSON object.

Required fields (set null if not present, use 0 for missing numeric fields):
{
  "gross_salary": <annual gross salary>,
  "basic_salary": <basic salary component>,
  "hra_received": <HRA allowance received>,
  "lta": <Leave Travel Allowance>,
  "special_allowance": <special allowance>,
  "standard_deduction": <standard deduction, default 50000>,
  "professional_tax": <professional tax paid>,
  "section_80c_investments": {
    "pf": <Provident Fund contribution>,
    "ppf": <PPF>,
    "elss": <ELSS mutual funds>,
    "lic_premium": <LIC premium>,
    "nsc": <NSC>,
    "home_loan_principal": <home loan principal repayment>,
    "tuition_fees": <tuition fees>,
    "total": <sum of all 80C>
  },
  "section_80d_premium": {
    "self_family": <health insurance for self/family>,
    "parents": <health insurance for parents>,
    "total": <sum>
  },
  "home_loan_interest": <interest on home loan (Section 24b)>,
  "education_loan_interest": <Section 80E>,
  "nps_contribution": <NPS contribution 80CCD(1B)>,
  "total_tds_deducted": <total TDS deducted>,
  "employer_name": "<employer name>",
  "pan_number": "<PAN if present, else null>",
  "assessment_year": "<AY e.g. 2025-26>"
}

Rules:
- Return ONLY the JSON object, no markdown, no explanation
- All rupee amounts must be annual figures
- If TDS is monthly, multiply by 12
- Set totals to sum of their components
"""


async def parse_pdf_agent(pdf_bytes: bytes) -> ParsedFormData:
    """
    Parse a Form 16 PDF and return structured financial data.
    Falls back to a demo dataset if LLM keys are not configured.
    """
    try:
        raw_text = extract_text_from_bytes(pdf_bytes)
        logger.info(f"Extracted {len(raw_text)} characters from PDF")
    except Exception as e:
        logger.warning(f"PDF extraction failed, using manual input: {e}")
        raw_text = "Could not extract PDF text. Please rely on manual income entry."

    if not settings.OPENAI_API_KEY:
        logger.warning("No OpenAI API key, returning demo data")
        return _demo_form_data()

    try:
        response = await llm_call(
            model=settings.PDF_PARSER_MODEL,
            system_prompt=SYSTEM_PROMPT,
            user_message=f"Parse this Form 16 document:\n\n{raw_text[:8000]}",
            temperature=0.0,
            max_tokens=2000,
        )

        # Clean JSON
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]

        data = json.loads(response)
        return _dict_to_parsed_form(data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from LLM: {e}")
        return _demo_form_data()
    except Exception as e:
        logger.error(f"PDF Parser Agent failed: {e}")
        return _demo_form_data()


def _dict_to_parsed_form(data: dict) -> ParsedFormData:
    c = data.get("section_80c_investments", {}) or {}
    d = data.get("section_80d_premium", {}) or {}

    c_total = sum([
        float(c.get("pf", 0) or 0),
        float(c.get("ppf", 0) or 0),
        float(c.get("elss", 0) or 0),
        float(c.get("lic_premium", 0) or 0),
        float(c.get("nsc", 0) or 0),
        float(c.get("home_loan_principal", 0) or 0),
        float(c.get("tuition_fees", 0) or 0),
    ])

    d_total = sum([
        float(d.get("self_family", 0) or 0),
        float(d.get("parents", 0) or 0),
    ])

    return ParsedFormData(
        gross_salary=float(data.get("gross_salary", 0) or 0),
        basic_salary=float(data.get("basic_salary", 0) or 0),
        hra_received=float(data.get("hra_received", 0) or 0),
        lta=float(data.get("lta", 0) or 0),
        special_allowance=float(data.get("special_allowance", 0) or 0),
        standard_deduction=float(data.get("standard_deduction", 50000) or 50000),
        professional_tax=float(data.get("professional_tax", 0) or 0),
        section_80c_investments=Section80CBreakdown(
            pf=float(c.get("pf", 0) or 0),
            ppf=float(c.get("ppf", 0) or 0),
            elss=float(c.get("elss", 0) or 0),
            lic_premium=float(c.get("lic_premium", 0) or 0),
            nsc=float(c.get("nsc", 0) or 0),
            home_loan_principal=float(c.get("home_loan_principal", 0) or 0),
            tuition_fees=float(c.get("tuition_fees", 0) or 0),
            total=c_total,
        ),
        section_80d_premium=Section80DBreakdown(
            self_family=float(d.get("self_family", 0) or 0),
            parents=float(d.get("parents", 0) or 0),
            total=d_total,
        ),
        home_loan_interest=float(data.get("home_loan_interest", 0) or 0),
        education_loan_interest=float(data.get("education_loan_interest", 0) or 0),
        nps_contribution=float(data.get("nps_contribution", 0) or 0),
        total_tds_deducted=float(data.get("total_tds_deducted", 0) or 0),
        employer_name=data.get("employer_name"),
        pan_number=data.get("pan_number"),
        assessment_year=data.get("assessment_year", "2025-26"),
    )


def _demo_form_data() -> ParsedFormData:
    """Returns realistic demo data for Priya (₹12 LPA developer)."""
    return ParsedFormData(
        gross_salary=1_200_000,
        basic_salary=600_000,
        hra_received=240_000,
        lta=50_000,
        special_allowance=310_000,
        standard_deduction=50_000,
        professional_tax=2_400,
        section_80c_investments=Section80CBreakdown(
            pf=72_000, ppf=0, elss=0, lic_premium=15_000,
            nsc=0, home_loan_principal=0, tuition_fees=0, total=87_000
        ),
        section_80d_premium=Section80DBreakdown(
            self_family=12_000, parents=0, total=12_000
        ),
        home_loan_interest=0,
        education_loan_interest=0,
        nps_contribution=0,
        total_tds_deducted=82_000,
        employer_name="Tech Corp Pvt Ltd",
        pan_number="ABCDE1234F",
        assessment_year="2025-26",
    )
