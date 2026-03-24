# agents/pdf_parser_agent.py
"""
PDF Parser Agent
Uses GPT-4 Vision to extract structured data from Form 16 PDFs.
Strategy:
  1. Extract text with pdfplumber
  2. If text is rich  → GPT-4 text mode
  3. If text is poor  → Convert pages to images → GPT-4 Vision
"""

import json
import logging
import base64
from io import BytesIO
from typing import Any

import pdfplumber
from pdf2image import convert_from_bytes
from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

# ── Prompt Templates ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert Indian tax document analyst.
Your job is to extract financial data from Form 16 documents with
100% accuracy. All amounts are in Indian Rupees (₹).
Return ONLY valid JSON — no markdown, no explanation.
""".strip()

TEXT_EXTRACTION_PROMPT = """
Extract all tax-related data from this Form 16 document text.

Return a JSON object with these exact keys:

{
  "employer_name": "string",
  "employer_tan": "string",
  "employee_name": "string",
  "employee_pan": "string (first 5 chars + XXXXX for privacy)",
  "assessment_year": "string (e.g. 2025-26)",
  "gross_salary": number,
  "exemptions_section_10": {
    "hra": number,
    "lta": number,
    "other": number
  },
  "standard_deduction": number,
  "professional_tax": number,
  "income_from_house_property": number,
  "deductions_chapter_vi_a": {
    "section_80c": number,
    "section_80ccc": number,
    "section_80ccd_1": number,
    "section_80ccd_1b": number,
    "section_80ccd_2": number,
    "section_80d": number,
    "section_80e": number,
    "section_80g": number,
    "section_80tta": number,
    "other_deductions": number
  },
  "total_taxable_income": number,
  "total_tax_liability": number,
  "tds_deducted": number,
  "tax_payable_or_refundable": number,
  "extraction_confidence": "high | medium | low",
  "notes": ["any assumptions or missing fields"]
}

Rules:
- Remove commas and ₹ from numbers
- Use 0 for any missing numeric field
- Use "Not Found" for missing text fields

Document text:
{document_text}
""".strip()

IMAGE_EXTRACTION_PROMPT = """
This is a page from an Indian Form 16 income tax document.

Extract ALL visible tax data. Return JSON with this structure:
{
  "employer_name": "string",
  "gross_salary": number,
  "exemptions_section_10": { "hra": number, "lta": number, "other": number },
  "standard_deduction": number,
  "professional_tax": number,
  "deductions_chapter_vi_a": {
    "section_80c": number,
    "section_80ccd_1b": number,
    "section_80d": number,
    "section_80e": number,
    "section_80g": number,
    "section_80tta": number
  },
  "total_taxable_income": number,
  "tds_deducted": number,
  "extraction_confidence": "high | medium | low"
}

Use 0 for any field not visible. Return ONLY JSON.
""".strip()


# ── Agent Class ───────────────────────────────────────────────────────────────

class PDFParserAgent:
    """
    Extracts structured tax data from Form 16 PDFs using GPT-4 (Vision).
    """

    MIN_TEXT_LENGTH = 300   # chars — below this we switch to vision mode
    MAX_TEXT_CHARS  = 14000 # chars — truncate to avoid token limits
    MAX_PDF_PAGES   = 6     # only process first N pages
    IMAGE_DPI       = 150   # DPI for PDF → image conversion

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # ── Public API ────────────────────────────────────────────────────────────

    async def parse(self, pdf_content: bytes) -> dict[str, Any]:
        """
        Main entry point.
        Tries text extraction first, falls back to vision if needed.
        """
        logger.info("[PDFParser] Starting PDF parse")

        # Step 1: Try text-based extraction
        text = self._extract_text(pdf_content)
        logger.info(f"[PDFParser] Extracted text length: {len(text)} chars")

        if len(text) >= self.MIN_TEXT_LENGTH:
            logger.info("[PDFParser] Using text-mode extraction (GPT-4)")
            raw = await self._extract_from_text(text)
        else:
            logger.info("[PDFParser] Text too short — using vision-mode (GPT-4V)")
            raw = await self._extract_from_images(pdf_content)

        # Step 2: Validate & normalize
        result = self._normalize(raw)
        logger.info(
            f"[PDFParser] Done. Gross salary: ₹{result.get('gross_salary', 0):,.0f} "
            f"| Confidence: {result.get('extraction_confidence', 'unknown')}"
        )
        return result

    # ── Text Extraction ───────────────────────────────────────────────────────

    def _extract_text(self, pdf_content: bytes) -> str:
        """
        Extract raw text from PDF using pdfplumber.
        Also captures table rows for Form 16 structured sections.
        """
        parts: list[str] = []

        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                for i, page in enumerate(pdf.pages[:self.MAX_PDF_PAGES]):
                    # Plain text
                    text = page.extract_text()
                    if text:
                        parts.append(text)

                    # Tables (Form 16 has many)
                    for table in (page.extract_tables() or []):
                        for row in table:
                            if row:
                                cleaned = " | ".join(
                                    str(cell).strip() for cell in row if cell
                                )
                                if cleaned:
                                    parts.append(cleaned)

        except Exception as e:
            logger.warning(f"[PDFParser] Text extraction error: {e}")

        return "\n".join(parts)

    async def _extract_from_text(self, text: str) -> dict:
        """
        Use GPT-4 to extract structured JSON from plain text.
        """
        truncated = text[:self.MAX_TEXT_CHARS]

        prompt = TEXT_EXTRACTION_PROMPT.format(document_text=truncated)

        response = await self.client.chat.completions.create(
            model            = settings.PRIMARY_MODEL,
            temperature      = 0.1,
            max_tokens       = 2048,
            response_format  = {"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ]
        )

        return self._safe_json(response.choices[0].message.content)

    # ── Vision Extraction ─────────────────────────────────────────────────────

    async def _extract_from_images(self, pdf_content: bytes) -> dict:
        """
        Convert PDF pages to images and use GPT-4 Vision to extract data.
        Merges results from all pages.
        """
        try:
            images = convert_from_bytes(
                pdf_content,
                dpi          = self.IMAGE_DPI,
                first_page   = 1,
                last_page    = self.MAX_PDF_PAGES,
            )
        except Exception as e:
            logger.error(f"[PDFParser] PDF→image conversion failed: {e}")
            return {}

        all_results: list[dict] = []

        for i, image in enumerate(images):
            # Resize to reduce token cost
            image.thumbnail((1400, 1900))

            # Convert to base64 PNG
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            logger.info(f"[PDFParser] Processing image page {i + 1}")

            try:
                response = await self.client.chat.completions.create(
                    model       = settings.VISION_MODEL,
                    temperature = 0.1,
                    max_tokens  = 2048,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": IMAGE_EXTRACTION_PROMPT,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url":    f"data:image/png;base64,{b64}",
                                        "detail": "high",
                                    },
                                },
                            ],
                        }
                    ],
                )
                page_data = self._safe_json(response.choices[0].message.content)
                if page_data:
                    all_results.append(page_data)

            except Exception as e:
                logger.warning(f"[PDFParser] Vision extraction error on page {i+1}: {e}")

        return self._merge_page_results(all_results)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _merge_page_results(self, results: list[dict]) -> dict:
        """
        Merge extracted data from multiple PDF pages.
        Prefers first non-zero / non-null value for each field.
        """
        if not results:
            return {}

        merged = results[0].copy()

        for page in results[1:]:
            for key, val in page.items():
                existing = merged.get(key)

                # Replace zero numbers with non-zero values from later pages
                if isinstance(val, (int, float)) and val > 0:
                    if not isinstance(existing, (int, float)) or existing == 0:
                        merged[key] = val

                # Merge nested dicts
                elif isinstance(val, dict) and isinstance(existing, dict):
                    for k, v in val.items():
                        if isinstance(v, (int, float)) and v > 0:
                            if not isinstance(existing.get(k), (int, float)) or existing.get(k, 0) == 0:
                                merged[key][k] = v

                # Replace "Not Found" strings
                elif isinstance(val, str) and val not in ("", "Not Found"):
                    if not isinstance(existing, str) or existing in ("", "Not Found"):
                        merged[key] = val

        return merged

    def _normalize(self, data: dict) -> dict:
        """
        Validate and normalize extracted data.
        Ensures all required fields exist with correct types.
        """
        # Default structure
        defaults: dict[str, Any] = {
            "employer_name":               "Unknown",
            "employer_tan":                "Not Found",
            "employee_name":               "Taxpayer",
            "employee_pan":                "XXXXX0000X",
            "assessment_year":             "2025-26",
            "gross_salary":                0.0,
            "exemptions_section_10":       {"hra": 0.0, "lta": 0.0, "other": 0.0},
            "standard_deduction":          50000.0,
            "professional_tax":            0.0,
            "income_from_house_property":  0.0,
            "deductions_chapter_vi_a": {
                "section_80c":     0.0,
                "section_80ccc":   0.0,
                "section_80ccd_1": 0.0,
                "section_80ccd_1b":0.0,
                "section_80ccd_2": 0.0,
                "section_80d":     0.0,
                "section_80e":     0.0,
                "section_80g":     0.0,
                "section_80tta":   0.0,
                "other_deductions":0.0,
            },
            "total_taxable_income":        0.0,
            "total_tax_liability":         0.0,
            "tds_deducted":                0.0,
            "tax_payable_or_refundable":   0.0,
            "extraction_confidence":       "low",
            "notes":                       [],
        }

        # Fill missing keys
        for key, default_val in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default_val
            elif isinstance(default_val, dict) and isinstance(data[key], dict):
                for k, v in default_val.items():
                    if k not in data[key] or data[key][k] is None:
                        data[key][k] = v

        # Convert all numeric strings to float
        data = self._deep_to_float(data)

        return data

    def _deep_to_float(self, obj: Any) -> Any:
        """
        Recursively convert string numbers → float in nested dicts/lists.
        """
        if isinstance(obj, dict):
            return {k: self._deep_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_to_float(i) for i in obj]
        elif isinstance(obj, str):
            cleaned = obj.replace(",", "").replace("₹", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return obj
        return obj

    def _safe_json(self, text: str) -> dict:
        """
        Safely parse JSON from LLM response.
        Strips markdown code fences if present.
        """
        if not text:
            return {}

        # Strip markdown fences
        for fence in ("```json", "```"):
            if fence in text:
                text = text.split(fence)[-1].split("```")[0]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"[PDFParser] JSON parse error: {e}")
            return {}