"""
Tax Regime Advisor Agent - Old vs New comparison
"""

import json
from typing import Dict, Any

from services.llm_gateway import llm
from prompts.regime_advisor import SYSTEM_PROMPT, COMPARISON_PROMPT
from config import settings


class RegimeAdvisorAgent:
    """
    AI agent that compares Old vs New tax regimes
    
    Uses GPT-4 for precise calculations with validation
    """
    
    def __init__(self):
        # Tax slabs FY 2024-25
        self.old_slabs = [
            (250000, 0),
            (500000, 0.05),
            (1000000, 0.20),
            (float('inf'), 0.30)
        ]
        
        self.new_slabs = [
            (300000, 0),
            (700000, 0.05),
            (1000000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float('inf'), 0.30)
        ]
    
    async def compare(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare tax under old and new regimes
        """
        # Extract required data
        gross_salary = tax_data.get("gross_salary", 0)
        deductions = self._extract_deductions(tax_data)
        
        # First, calculate ourselves (for validation)
        calculated = self._calculate_both_regimes(gross_salary, deductions)
        
        # Then use AI for detailed analysis and recommendations
        prompt = self._build_prompt(tax_data, deductions)
        
        ai_response = await llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            json_mode=True
        )
        
        try:
            ai_analysis = json.loads(ai_response)
        except json.JSONDecodeError:
            ai_analysis = {}
        
        # Merge calculated values with AI analysis
        result = self._merge_results(calculated, ai_analysis)
        
        return result
    
    def _extract_deductions(self, tax_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract all deductions for old regime calculation
        """
        chapter_vi = tax_data.get("deductions_chapter_vi_a", {})
        exemptions = tax_data.get("exemptions_section_10", {})
        
        return {
            "standard_deduction": 50000,
            "section_80c": min(chapter_vi.get("section_80c", 0), 150000),
            "section_80ccd_1b": min(chapter_vi.get("section_80ccd_1b", 0), 50000),
            "section_80d": min(chapter_vi.get("section_80d", 0), 100000),
            "home_loan_interest": min(tax_data.get("home_loan_interest", 0), 200000),
            "hra_exemption": exemptions.get("hra", 0),
            "lta_exemption": exemptions.get("lta", 0),
            "professional_tax": tax_data.get("professional_tax", 0),
        }
    
    def _calculate_both_regimes(
        self, 
        gross_salary: float, 
        deductions: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate tax for both regimes
        """
        # OLD REGIME
        old_total_deductions = sum(deductions.values())
        old_taxable = max(0, gross_salary - old_total_deductions)
        old_tax = self._calculate_tax(old_taxable, self.old_slabs)
        old_tax = self._apply_rebate(old_tax, old_taxable, "old")
        old_tax_with_cess = old_tax * 1.04
        
        # NEW REGIME
        new_deductions = 75000  # Only standard deduction in new regime
        new_taxable = max(0, gross_salary - new_deductions)
        new_tax = self._calculate_tax(new_taxable, self.new_slabs)
        new_tax = self._apply_rebate(new_tax, new_taxable, "new")
        new_tax_with_cess = new_tax * 1.04
        
        # Determine better regime
        if old_tax_with_cess < new_tax_with_cess:
            better = "OLD"
            savings = new_tax_with_cess - old_tax_with_cess
        elif new_tax_with_cess < old_tax_with_cess:
            better = "NEW"
            savings = old_tax_with_cess - new_tax_with_cess
        else:
            better = "SAME"
            savings = 0
        
        return {
            "old_regime": {
                "total_deductions": old_total_deductions,
                "taxable_income": old_taxable,
                "tax_before_cess": round(old_tax, 2),
                "cess": round(old_tax * 0.04, 2),
                "total_tax": round(old_tax_with_cess, 2)
            },
            "new_regime": {
                "total_deductions": new_deductions,
                "taxable_income": new_taxable,
                "tax_before_cess": round(new_tax, 2),
                "cess": round(new_tax * 0.04, 2),
                "total_tax": round(new_tax_with_cess, 2)
            },
            "comparison": {
                "old_regime_tax": round(old_tax_with_cess, 2),
                "new_regime_tax": round(new_tax_with_cess, 2),
                "better_regime": better,
                "savings_amount": round(savings, 2)
            }
        }
    
    def _calculate_tax(self, taxable_income: float, slabs: list) -> float:
        """
        Calculate tax based on slabs
        """
        tax = 0
        prev_limit = 0
        
        for limit, rate in slabs:
            if taxable_income <= prev_limit:
                break
            
            taxable_in_slab = min(taxable_income, limit) - prev_limit
            tax += taxable_in_slab * rate
            prev_limit = limit
        
        return tax
    
    def _apply_rebate(self, tax: float, taxable_income: float, regime: str) -> float:
        """
        Apply Section 87A rebate
        """
        if regime == "new":
            # New regime: Full rebate if taxable income <= 7L
            if taxable_income <= 700000:
                return 0
        else:
            # Old regime: Rebate up to 12,500 if taxable income <= 5L
            if taxable_income <= 500000:
                return max(0, tax - 12500)
        
        return tax
    
    def _build_prompt(self, tax_data: Dict[str, Any], deductions: Dict[str, float]) -> str:
        """
        Build prompt for AI analysis
        """
        return COMPARISON_PROMPT.format(
            gross_salary=tax_data.get("gross_salary", 0),
            age=tax_data.get("age", 30),
            standard_deduction=deductions.get("standard_deduction", 50000),
            section_80c=deductions.get("section_80c", 0),
            section_80ccd_1b=deductions.get("section_80ccd_1b", 0),
            section_80d=deductions.get("section_80d", 0),
            home_loan_interest=deductions.get("home_loan_interest", 0),
            hra_exemption=deductions.get("hra_exemption", 0),
            lta_exemption=deductions.get("lta_exemption", 0),
            professional_tax=deductions.get("professional_tax", 0),
            other_deductions=0
        )
    
    def _merge_results(
        self, 
        calculated: Dict[str, Any], 
        ai_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge calculated results with AI analysis
        """
        # Start with calculated values (more reliable)
        result = calculated.copy()
        
        # Add AI recommendations if available
        if "recommendation" in ai_analysis:
            result["recommendation"] = ai_analysis["recommendation"]
        else:
            # Generate basic recommendation
            better = calculated["comparison"]["better_regime"]
            savings = calculated["comparison"]["savings_amount"]
            
            result["recommendation"] = {
                "regime": better,
                "confidence": "HIGH" if savings > 10000 else "MEDIUM",
                "primary_reason": self._get_recommendation_reason(better, savings, calculated)
            }
        
        if "what_if_scenarios" in ai_analysis:
            result["what_if_scenarios"] = ai_analysis["what_if_scenarios"]
        
        return result
    