"""
TaxGenie AI - Tax Calculator Service
Pure Python deterministic tax calculations for FY 2024-25 / AY 2025-26.
"""

from models.response_models import ParsedFormData, RegimeBreakdown, RegimeComparison


def calculate_old_regime_tax(taxable_income: float) -> float:
    """Calculate tax under Old Regime FY 2024-25 (slabs)."""
    tax = 0.0
    if taxable_income <= 250_000:
        tax = 0
    elif taxable_income <= 500_000:
        tax = (taxable_income - 250_000) * 0.05
    elif taxable_income <= 1_000_000:
        tax = 12_500 + (taxable_income - 500_000) * 0.20
    else:
        tax = 112_500 + (taxable_income - 1_000_000) * 0.30
    return tax


def calculate_new_regime_tax(taxable_income: float) -> float:
    """Calculate tax under New Regime FY 2024-25."""
    tax = 0.0
    if taxable_income <= 300_000:
        tax = 0
    elif taxable_income <= 600_000:
        tax = (taxable_income - 300_000) * 0.05
    elif taxable_income <= 900_000:
        tax = 15_000 + (taxable_income - 600_000) * 0.10
    elif taxable_income <= 1_200_000:
        tax = 45_000 + (taxable_income - 900_000) * 0.15
    elif taxable_income <= 1_500_000:
        tax = 90_000 + (taxable_income - 1_200_000) * 0.20
    else:
        tax = 150_000 + (taxable_income - 1_500_000) * 0.30
    return tax


def apply_rebate_87a(tax: float, taxable_income: float, regime: str) -> float:
    """Apply Section 87A rebate. Max ₹12,500 if income ≤ ₹5L (old) or ₹25,000 if ≤ ₹7L (new)."""
    if regime == "old" and taxable_income <= 500_000:
        return max(0, tax - 12_500)
    if regime == "new" and taxable_income <= 700_000:
        return max(0, tax - 25_000)
    return tax


def add_cess(tax: float) -> tuple[float, float]:
    """Add 4% Health & Education Cess."""
    cess = round(tax * 0.04, 2)
    return round(tax + cess, 2), cess


def compute_old_regime(data: ParsedFormData) -> RegimeBreakdown:
    gross = data.gross_salary
    breakdown = {}

    deductions = 0
    breakdown["standard_deduction"] = data.standard_deduction
    deductions += data.standard_deduction

    breakdown["professional_tax"] = data.professional_tax
    deductions += data.professional_tax

    c_total = data.section_80c_investments.total
    c_applied = min(c_total, 150_000)
    breakdown["section_80c"] = c_applied
    deductions += c_applied

    d_total = data.section_80d_premium.total
    d_applied = min(d_total, 50_000)
    breakdown["section_80d"] = d_applied
    deductions += d_applied

    if data.home_loan_interest > 0:
        hl_applied = min(data.home_loan_interest, 200_000)
        breakdown["home_loan_interest_24b"] = hl_applied
        deductions += hl_applied

    if data.education_loan_interest > 0:
        breakdown["education_loan_interest_80e"] = data.education_loan_interest
        deductions += data.education_loan_interest

    if data.nps_contribution > 0:
        nps_applied = min(data.nps_contribution, 50_000)
        breakdown["nps_80ccd1b"] = nps_applied
        deductions += nps_applied

    taxable = max(0, gross - deductions)
    raw_tax = calculate_old_regime_tax(taxable)
    after_rebate = apply_rebate_87a(raw_tax, taxable, "old")
    total_tax, cess = add_cess(after_rebate)

    return RegimeBreakdown(
        gross_income=gross,
        total_deductions=deductions,
        taxable_income=taxable,
        tax_before_cess=after_rebate,
        health_education_cess=cess,
        total_tax=total_tax,
        breakdown=breakdown
    )


def compute_new_regime(data: ParsedFormData) -> RegimeBreakdown:
    gross = data.gross_salary
    standard_ded = 75_000  # New regime standard deduction FY 2024-25

    taxable = max(0, gross - standard_ded)
    raw_tax = calculate_new_regime_tax(taxable)
    after_rebate = apply_rebate_87a(raw_tax, taxable, "new")
    total_tax, cess = add_cess(after_rebate)

    return RegimeBreakdown(
        gross_income=gross,
        total_deductions=standard_ded,
        taxable_income=taxable,
        tax_before_cess=after_rebate,
        health_education_cess=cess,
        total_tax=total_tax,
        breakdown={"standard_deduction_new": standard_ded}
    )


def calculate_breakeven_deductions(gross: float) -> float:
    """Calculate what total deductions would make Old and New Regime equal."""
    # Approximate breakeven (iterative approach)
    new_taxable = max(0, gross - 75_000)
    new_tax_base = calculate_new_regime_tax(new_taxable)

    # Binary search for breakeven
    lo, hi = 75_000.0, 1_000_000.0
    for _ in range(50):
        mid = (lo + hi) / 2
        old_taxable = max(0, gross - mid)
        old_tax = calculate_old_regime_tax(old_taxable)
        if old_tax > new_tax_base:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 0)


def compare_regimes(data: ParsedFormData) -> RegimeComparison:
    old = compute_old_regime(data)
    new = compute_new_regime(data)

    if new.total_tax < old.total_tax:
        recommended = "NEW"
        savings = round(old.total_tax - new.total_tax, 2)
        reason = (
            f"New Regime saves ₹{savings:,.0f} because your current deductions "
            f"(₹{old.total_deductions:,.0f}) don't offset the lower slab rates."
        )
    else:
        recommended = "OLD"
        savings = round(new.total_tax - old.total_tax, 2)
        reason = (
            f"Old Regime saves ₹{savings:,.0f} because your deductions "
            f"(₹{old.total_deductions:,.0f}) significantly reduce your taxable income."
        )

    breakeven = calculate_breakeven_deductions(data.gross_salary)

    return RegimeComparison(
        old_regime=old,
        new_regime=new,
        recommended_regime=recommended,
        savings_with_recommended=savings,
        recommendation_reason=reason,
        breakeven_deduction_amount=breakeven
    )
