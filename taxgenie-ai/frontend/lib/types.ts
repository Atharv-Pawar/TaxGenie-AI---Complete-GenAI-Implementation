export interface TaxData {
  gross_salary: number;
  hra_received: number;
  lta_received: number;
  standard_deduction: number;
  section_80c: number;
  section_80ccd_1b: number;
  section_80d: number;
  home_loan_interest: number;
  professional_tax: number;
  tds_deducted: number;
}

export interface MissedDeduction {
  section: string;
  description: string;
  current_claimed: number;
  max_limit: number;
  unused_limit: number;
  potential_tax_saving: number;
  how_to_claim: string[];
  priority: "HIGH" | "MEDIUM" | "LOW";
}

export interface RegimeComparison {
  old_regime_tax: number;
  new_regime_tax: number;
  recommendation: {
    regime: "OLD" | "NEW";
    confidence: "HIGH" | "MEDIUM" | "LOW";
    primary_reason: string;
  };
}

export interface AnalysisResult {
  tax_data: TaxData;
  missed_deductions: MissedDeduction[];
  regime_comparison: RegimeComparison;
  investment_recommendations: any[];
  summary: string;
}