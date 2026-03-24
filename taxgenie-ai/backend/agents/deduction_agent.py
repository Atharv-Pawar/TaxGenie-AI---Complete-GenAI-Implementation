"""
Deduction Finder Agent - Uses Claude for thorough analysis
"""

import json
from typing import Dict, List, Any

from services.llm_gateway import llm
from rag.knowledge_base import knowledge_base
from prompts.deduction_finder import SYSTEM_PROMPT, ANALYSIS_PROMPT, OPPORTUNITY_SCHEMA
from config import settings


class DeductionFinderAgent:
    """
    AI agent that analyzes tax data to find missed deductions
    
    Uses:
    - Claude 3.5 Sonnet for reasoning
    - RAG for tax rules lookup
    """
    
    def __init__(self):
        self.deduction_limits = {
            "section_80c": 150000,
            "section_80ccd_1b": 50000,
            "section_80d_self": 25000,
            "section_80d_self_senior": 50000,
            "section_80d_parents": 25000,
            "section_80d_parents_senior": 50000,
            "section_80tta": 10000,
            "section_80ttb": 50000,  # For seniors
            "section_24": 200000,
            "section_80e": float('inf'),  # No limit
            "section_80g": float('inf'),  # Up to 10% GTI
        }
    
    async def analyze(self, tax_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze tax data and find all missed deductions
        """
        # Get current deductions from tax data
        current_deductions = self._extract_current_deductions(tax_data)
        
        # Get relevant tax rules from RAG
        tax_context = await self._get_tax_context(tax_data)
        
        # Build the analysis prompt
        prompt = self._build_prompt(tax_data, current_deductions, tax_context)
        
        # Use Claude for analysis (better at reasoning)
        model = settings.CLAUDE_MODEL if settings.ANTHROPIC_API_KEY else settings.PRIMARY_MODEL
        
        response = await llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            temperature=0.3,
            max_tokens=4096
        )
        
        # Parse response
        opportunities = self._parse_opportunities(response)
        
        # Validate and enhance with calculated values
        opportunities = self._validate_opportunities(opportunities, tax_data)
        
        return opportunities
    
    def _extract_current_deductions(self, tax_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract current deductions from tax data
        """
        deductions = tax_data.get("deductions_chapter_vi_a", {})
        exemptions = tax_data.get("exemptions_section_10", {})
        
        return {
            "section_80c": deductions.get("section_80c", 0) + 
                          deductions.get("section_80ccc", 0) + 
                          deductions.get("section_80ccd_1", 0),
            "section_80ccd_1b": deductions.get("section_80ccd_1b", 0),
            "section_80d": deductions.get("section_80d", 0),
            "section_80e": deductions.get("section_80e", 0),
            "section_80g": deductions.get("section_80g", 0),
            "section_80tta": deductions.get("section_80tta", 0),
            "section_24": tax_data.get("section_24_home_loan", 0) or 
                         tax_data.get("home_loan_interest", 0),
            "hra_exemption": exemptions.get("hra", 0),
            "lta_exemption": exemptions.get("lta", 0),
            "standard_deduction": tax_data.get("standard_deduction", 50000),
            "professional_tax": tax_data.get("professional_tax", 0),
        }
    
    async def _get_tax_context(self, tax_data: Dict[str, Any]) -> str:
        """
        Get relevant tax rules from knowledge base
        """
        gross_salary = tax_data.get("gross_salary", 0)
        
        # Build query based on user's situation
        queries = [
            f"tax deductions for salary income {gross_salary}",
            "80C 80D 80CCD investment options",
            "HRA LTA exemptions rules"
        ]
        
        context_parts = []
        for query in queries:
            results = await knowledge_base.search(query, k=2)
            for doc in results:
                context_parts.append(doc.page_content)
        
        return "\n\n---\n\n".join(context_parts[:5])  # Limit context size
    
    def _build_prompt(
        self, 
        tax_data: Dict[str, Any], 
        current: Dict[str, float],
        tax_context: str
    ) -> str:
        """
        Build the analysis prompt
        """
        prompt = ANALYSIS_PROMPT.format(
            gross_salary=tax_data.get("gross_salary", 0),
            regime="Old Regime",  # Assume old for deduction analysis
            section_80c=current.get("section_80c", 0),
            section_80ccd_1b=current.get("section_80ccd_1b", 0),
            section_80d=current.get("section_80d", 0),
            home_loan_interest=current.get("section_24", 0),
            hra_exemption=current.get("hra_exemption", 0),
            lta_exemption=current.get("lta_exemption", 0),
            professional_tax=current.get("professional_tax", 0),
            tax_context=tax_context
        )
        
        prompt += f"\n\nExpected JSON schema:\n{OPPORTUNITY_SCHEMA}"
        
        return prompt
    
    def _parse_opportunities(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse AI response into structured opportunities
        """
        try:
            # Try direct JSON parse
            if "{" in response:
                # Find JSON in response
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get("opportunities", [])
        except json.JSONDecodeError:
            pass
        
        # Fallback: return empty list
        return []
    
    def _validate_opportunities(
        self, 
        opportunities: List[Dict], 
        tax_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Validate and recalculate tax savings
        """
        gross_salary = tax_data.get("gross_salary", 0)
        
        # Determine tax bracket
        if gross_salary <= 500000:
            tax_rate = 0.05
        elif gross_salary <= 1000000:
            tax_rate = 0.20
        else:
            tax_rate = 0.30
        
        # Add cess
        effective_rate = tax_rate * 1.04
        
        validated = []
        for opp in opportunities:
            # Recalculate tax saving with correct rate
            unused = opp.get("unused_limit", 0)
            if unused > 0:
                opp["potential_tax_saving"] = round(unused * effective_rate, 2)
                opp["tax_bracket_used"] = f"{tax_rate*100:.0f}% + 4% cess"
                validated.append(opp)
        
        # Sort by potential savings
        validated.sort(key=lambda x: x.get("potential_tax_saving", 0), reverse=True)
        
        return validated


# Create singleton
deduction_agent = DeductionFinderAgent()