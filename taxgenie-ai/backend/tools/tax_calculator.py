# tools/tax_calculator.py
"""
Tax Calculator Tool
Performs precise income tax calculations for Indian tax law (FY 2024-25).
Supports both Old and New regimes.
"""

from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class TaxResult:
    """Tax calculation result."""
    gross_income:      float
    total_deductions:  float
    taxable_income:    float
    gross_tax:         float
    rebate_87a:        float
    surcharge:         float
    cess:              float
    total_tax:         float
    effective_rate:    float
    regime:            str


class TaxCalculator:
    """
    Calculates Indian income tax with full compliance to FY 2024-25 rules.
    
    Features:
    - Old and New regime calculations
    - Section 87A rebate
    - Surcharge for high incomes
    - 4% Health & Education Cess
    - Age-based slab adjustments (senior/super-senior)
    """

    # ═══════════════════════════════════════════════════════════════════════
    # TAX SLABS FY 2024-25 (AY 2025-26)
    # ═══════════════════════════════════════════════════════════════════════

    # Old Regime - Regular (below 60 years)
    OLD_SLABS_REGULAR = [
        (250_000,    0.00),
        (500_000,    0.05),
        (1_000_000,  0.20),
        (float('inf'), 0.30),
    ]

    # Old Regime - Senior Citizen (60-80 years)
    OLD_SLABS_SENIOR = [
        (300_000,    0.00),
        (500_000,    0.05),
        (1_000_000,  0.20),
        (float('inf'), 0.30),
    ]

    # Old Regime - Super Senior (80+ years)
    OLD_SLABS_SUPER_SENIOR = [
        (500_000,    0.00),
        (1_000_000,  0.20),
        (float('inf'), 0.30),
    ]

    # New Regime (same for all ages)
    NEW_SLABS = [
        (300_000,    0.00),
        (700_000,    0.05),
        (1_000_000,  0.10),
        (1_200_000,  0.15),
        (1_500_000,  0.20),
        (float('inf'), 0.30),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # DEDUCTION LIMITS
    # ═══════════════════════════════════════════════════════════════════════

    STANDARD_DEDUCTION_OLD = 50_000
    STANDARD_DEDUCTION_NEW = 75_000

    DEDUCTION_LIMITS = {
        "80C":         150_000,
        "80CCD_1B":     50_000,
        "80CCD_2":     float('inf'),  # 14% of basic (employer NPS)
        "80D_self":     25_000,
        "80D_self_senior": 50_000,
        "80D_parents":  25_000,
        "80D_parents_senior": 50_000,
        "80E":         float('inf'),  # No limit
        "80G":         float('inf'),  # Varies
        "80TTA":        10_000,
        "80TTB":        50_000,       # For seniors
        "24B":         200_000,       # Home loan interest
    }

    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════

    def calculate(
        self,
        gross_income:  float,
        deductions:    dict,
        regime:        Literal["old", "new"] = "new",
        age_category:  Literal["regular", "senior", "super_senior"] = "regular",
    ) -> TaxResult:
        """
        Calculate total tax liability.

        Args:
            gross_income: Total gross salary
            deductions:   Dict of deduction amounts by section
            regime:       "old" or "new"
            age_category: "regular" (<60), "senior" (60-80), "super_senior" (80+)

        Returns:
            TaxResult with complete tax breakdown
        """

        # Select appropriate slabs
        if regime == "new":
            slabs = self.NEW_SLABS
            total_deductions = self.STANDARD_DEDUCTION_NEW
        else:
            if age_category == "super_senior":
                slabs = self.OLD_SLABS_SUPER_SENIOR
            elif age_category == "senior":
                slabs = self.OLD_SLABS_SENIOR
            else:
                slabs = self.OLD_SLABS_REGULAR

            total_deductions = self._calculate_old_regime_deductions(deductions)

        # Taxable income
        taxable_income = max(0, gross_income - total_deductions)

        # Calculate slab tax
        gross_tax = self._calculate_slab_tax(taxable_income, slabs)

        # Apply Section 87A rebate
        rebate_87a = self._apply_rebate_87a(gross_tax, taxable_income, regime)
        tax_after_rebate = max(0, gross_tax - rebate_87a)

        # Surcharge for high incomes
        surcharge = self._calculate_surcharge(tax_after_rebate, taxable_income)

        # 4% Cess
        cess = (tax_after_rebate + surcharge) * 0.04

        # Total tax
        total_tax = tax_after_rebate + surcharge + cess

        # Effective rate
        effective_rate = (total_tax / gross_income * 100) if gross_income > 0 else 0

        return TaxResult(
            gross_income     = round(gross_income, 2),
            total_deductions = round(total_deductions, 2),
            taxable_income   = round(taxable_income, 2),
            gross_tax        = round(gross_tax, 2),
            rebate_87a       = round(rebate_87a, 2),
            surcharge        = round(surcharge, 2),
            cess             = round(cess, 2),
            total_tax        = round(total_tax, 2),
            effective_rate   = round(effective_rate, 2),
            regime           = regime,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE CALCULATION METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def _calculate_old_regime_deductions(self, deductions: dict) -> float:
        """
        Calculate total deductions allowed under old regime.
        """
        total = self.STANDARD_DEDUCTION_OLD

        # 80C family
        total += min(deductions.get("80C", 0), self.DEDUCTION_LIMITS["80C"])

        # 80CCD(1B) - Additional NPS
        total += min(deductions.get("80CCD_1B", 0), self.DEDUCTION_LIMITS["80CCD_1B"])

        # 80CCD(2) - Employer NPS (no limit but capped at 14% of basic)
        total += deductions.get("80CCD_2", 0)

        # 80D - Health insurance
        d_self    = deductions.get("80D_self", 0)
        d_parents = deductions.get("80D_parents", 0)

        # Check if senior citizen rates apply
        is_self_senior    = deductions.get("is_self_senior", False)
        is_parents_senior = deductions.get("is_parents_senior", False)

        max_self    = self.DEDUCTION_LIMITS["80D_self_senior"] if is_self_senior else self.DEDUCTION_LIMITS["80D_self"]
        max_parents = self.DEDUCTION_LIMITS["80D_parents_senior"] if is_parents_senior else self.DEDUCTION_LIMITS["80D_parents"]

        total += min(d_self, max_self)
        total += min(d_parents, max_parents)

        # 80E - Education loan interest (no limit)
        total += deductions.get("80E", 0)

        # 80G - Donations
        total += deductions.get("80G", 0)

        # 80TTA/80TTB - Savings interest
        if deductions.get("age", 0) >= 60:
            total += min(deductions.get("80TTB", 0), self.DEDUCTION_LIMITS["80TTB"])
        else:
            total += min(deductions.get("80TTA", 0), self.DEDUCTION_LIMITS["80TTA"])

        # Section 24(b) - Home loan interest
        total += min(deductions.get("24B", 0), self.DEDUCTION_LIMITS["24B"])

        # HRA exemption
        total += deductions.get("HRA", 0)

        # LTA exemption
        total += deductions.get("LTA", 0)

        # Professional tax
        total += deductions.get("professional_tax", 0)

        return total

    def _calculate_slab_tax(self, taxable_income: float, slabs: list) -> float:
        """
        Calculate tax based on slab rates.
        """
        tax = 0.0
        previous_limit = 0

        for limit, rate in slabs:
            if taxable_income <= previous_limit:
                break

            taxable_in_slab = min(taxable_income, limit) - previous_limit
            tax += taxable_in_slab * rate
            previous_limit = limit

        return tax

    def _apply_rebate_87a(
        self,
        tax:            float,
        taxable_income: float,
        regime:         str,
    ) -> float:
        """
        Apply Section 87A rebate.

        New Regime: Full rebate if taxable income ≤ ₹7,00,000
        Old Regime: Rebate up to ₹12,500 if taxable income ≤ ₹5,00,000
        """
        if regime == "new":
            if taxable_income <= 700_000:
                return tax  # Full rebate
        else:
            if taxable_income <= 500_000:
                return min(tax, 12_500)  # Rebate capped at ₹12,500

        return 0.0

    def _calculate_surcharge(self, tax: float, taxable_income: float) -> float:
        """
        Calculate surcharge based on income level.

        Surcharge Slabs:
        - Up to ₹50L:    0%
        - ₹50L - ₹1Cr:   10%
        - ₹1Cr - ₹2Cr:   15%
        - ₹2Cr - ₹5Cr:   25%
        - Above ₹5Cr:    37%
        """
        if taxable_income <= 5_000_000:
            return 0.0
        elif taxable_income <= 10_000_000:
            return tax * 0.10
        elif taxable_income <= 20_000_000:
            return tax * 0.15
        elif taxable_income <= 50_000_000:
            return tax * 0.25
        else:
            return tax * 0.37

    # ═══════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def get_marginal_rate(
        self,
        taxable_income: float,
        regime:         Literal["old", "new"] = "new",
        age_category:   Literal["regular", "senior", "super_senior"] = "regular",
    ) -> float:
        """
        Get marginal tax rate (including cess) for a given income.
        Useful for calculating tax savings from additional deductions.
        """
        if regime == "new":
            slabs = self.NEW_SLABS
        else:
            if age_category == "super_senior":
                slabs = self.OLD_SLABS_SUPER_SENIOR
            elif age_category == "senior":
                slabs = self.OLD_SLABS_SENIOR
            else:
                slabs = self.OLD_SLABS_REGULAR

        # Find applicable slab
        for limit, rate in slabs:
            if taxable_income <= limit:
                return rate * 1.04  # Add 4% cess

        return 0.30 * 1.04  # Max rate with cess

    def estimate_tax_saving(
        self,
        additional_deduction: float,
        gross_income:         float,
        regime:               Literal["old", "new"] = "old",
    ) -> float:
        """
        Estimate tax saving from an additional deduction.
        Quick calculation without full tax computation.
        """
        # Simple estimation based on income bracket
        marginal_rate = self.get_marginal_rate(gross_income, regime)
        return additional_deduction * marginal_rate


# ════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ════════════════════════════════════════════════════════════════════════════

tax_calculator = TaxCalculator()