"""
PDF Parser Agent - Uses GPT-4 Vision for intelligent document extraction
"""

import pdfplumber
from pdf2image import convert_from_bytes
import json
from io import BytesIO
from typing import Dict, Any, List
import base64

from services.llm_gateway import llm
from prompts.pdf_parser import SYSTEM_PROMPT, EXTRACTION_PROMPT, IMAGE_EXTRACTION_PROMPT


class PDFParserAgent:
    """
    AI-powered PDF parser using GPT-4 Vision for Form 16 extraction
    
    Strategy:
    1. First attempt: Extract text and use GPT-4 to parse
    2. If text extraction fails: Convert to images and use GPT-4V
    3. Validate and clean extracted data
    """
    
    def __init__(self):
        self.max_image_size = (1500, 2000)  # Max dimensions for GPT-4V
    
    async def parse(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Parse Form 16 PDF and extract all tax data
        """
        # Step 1: Try text extraction first (faster, cheaper)
        text_content = self._extract_text(pdf_content)
        
        if text_content and len(text_content) > 500:
            # Good text content - use text-based extraction
            extracted = await self._extract_from_text(text_content)
        else:
            # Poor text content - use vision-based extraction
            extracted = await self._extract_from_images(pdf_content)
        
        # Step 2: Validate and enhance extracted data
        validated = self._validate_and_enhance(extracted)
        
        return validated
    
    def _extract_text(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF using pdfplumber
        """
        text_parts = []
        
        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    # Extract regular text
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                    
                    # Extract tables (important for Form 16)
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                row_text = " | ".join(str(cell or "") for cell in row)
                                text_parts.append(row_text)
        
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
        
        return "\n".join(text_parts)
    
    async def _extract_from_text(self, text_content: str) -> Dict[str, Any]:
        """
        Use GPT-4 to extract structured data from text
        """
        prompt = EXTRACTION_PROMPT.format(document_content=text_content[:15000])
        
        response = await llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.1,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            return self._parse_json_from_text(response)
    
    async def _extract_from_images(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Use GPT-4 Vision to extract data from PDF as images
        """
        # Convert PDF to images
        images = convert_from_bytes(pdf_content, dpi=150)
        
        all_extractions = []
        
        for i, image in enumerate(images[:5]):  # Limit to first 5 pages
            # Resize if needed
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                image.thumbnail(self.max_image_size)
            
            # Convert to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Use GPT-4V
            response = await llm.generate_with_image(
                prompt=IMAGE_EXTRACTION_PROMPT,
                image_data=img_bytes,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.1
            )
            
            try:
                page_data = json.loads(response)
                all_extractions.append(page_data)
            except:
                pass
        
        # Merge extractions from all pages
        return self._merge_extractions(all_extractions)
    
    def _merge_extractions(self, extractions: List[Dict]) -> Dict[str, Any]:
        """
        Merge extractions from multiple pages
        """
        if not extractions:
            return {}
        
        merged = extractions[0].copy()
        
        for ext in extractions[1:]:
            for key, value in ext.items():
                if key not in merged or merged[key] in [0, None, "Not Found"]:
                    merged[key] = value
                elif isinstance(value, dict):
                    # Merge nested dicts
                    if isinstance(merged.get(key), dict):
                        for k, v in value.items():
                            if k not in merged[key] or merged[key][k] in [0, None]:
                                merged[key][k] = v
        
        return merged
    
    def _validate_and_enhance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data and fill in calculated fields
        """
        # Ensure all required fields exist
        defaults = {
            "gross_salary": 0,
            "standard_deduction": 50000,
            "professional_tax": 0,
            "exemptions_section_10": {"hra": 0, "lta": 0, "other": 0},
            "deductions_chapter_vi_a": {
                "section_80c": 0,
                "section_80ccd_1b": 0,
                "section_80d": 0,
                "section_80e": 0,
                "section_80g": 0,
                "section_80tta": 0
            },
            "income_from_house_property": 0,
            "tds_deducted": 0
        }
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default_value
            elif isinstance(default_value, dict) and isinstance(data.get(key), dict):
                for k, v in default_value.items():
                    if k not in data[key] or data[key][k] is None:
                        data[key][k] = v
        
        # Calculate total deductions if not present
        if "total_deductions" not in data or data["total_deductions"] == 0:
            deductions = data.get("deductions_chapter_vi_a", {})
            data["total_deductions"] = sum(
                v for v in deductions.values() if isinstance(v, (int, float))
            )
        
        # Convert any string numbers to floats
        data = self._convert_to_numbers(data)
        
        return data
    
    def _convert_to_numbers(self, obj):
        """
        Recursively convert string numbers to floats
        """
        if isinstance(obj, dict):
            return {k: self._convert_to_numbers(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_numbers(item) for item in obj]
        elif isinstance(obj, str):
            # Try to convert to number
            cleaned = obj.replace(",", "").replace("₹", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return obj
        else:
            return obj
    
    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Try to extract JSON from text response
        """
        # Try to find JSON in the text
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {}