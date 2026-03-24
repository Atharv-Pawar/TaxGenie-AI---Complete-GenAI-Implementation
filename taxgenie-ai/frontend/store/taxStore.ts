import { create } from "zustand";

export type RiskProfile = "conservative" | "moderate" | "aggressive";
export type AnalysisStatus = "idle" | "uploading" | "processing" | "completed" | "failed";

export interface Section80CBreakdown {
  pf: number; ppf: number; elss: number; lic_premium: number;
  nsc: number; home_loan_principal: number; tuition_fees: number; total: number;
}
export interface Section80DBreakdown { self_family: number; parents: number; total: number; }

export interface ParsedFormData {
  gross_salary: number; basic_salary: number; hra_received: number;
  lta: number; special_allowance: number; standard_deduction: number;
  professional_tax: number; section_80c_investments: Section80CBreakdown;
  section_80d_premium: Section80DBreakdown; home_loan_interest: number;
  education_loan_interest: number; nps_contribution: number;
  total_tds_deducted: number; employer_name?: string;
  pan_number?: string; assessment_year: string;
}

export interface MissedDeduction {
  section: string; potential_saving: number; description: string;
  suggestions: string[]; urgency: "HIGH" | "MEDIUM" | "LOW";
}
export interface DeductionResult {
  claimed_deductions: { section: string; amount: number; description: string }[];
  missed_deductions: MissedDeduction[]; total_potential_savings: number;
}

export interface RegimeBreakdown {
  gross_income: number; total_deductions: number; taxable_income: number;
  tax_before_cess: number; health_education_cess: number; total_tax: number; breakdown: Record<string, number>;
}
export interface RegimeComparison {
  old_regime: RegimeBreakdown; new_regime: RegimeBreakdown;
  recommended_regime: "OLD" | "NEW"; savings_with_recommended: number;
  recommendation_reason: string; breakeven_deduction_amount: number;
}

export interface InvestmentRecommendation {
  instrument: string; section: string; recommended_amount: number;
  expected_returns: string; lock_in_period: string; risk_level: string;
  reason: string; top_picks: string[];
}

export interface AnalysisResult {
  session_id: string; status: AnalysisStatus;
  parsed_data?: ParsedFormData; missed_deductions?: DeductionResult;
  regime_comparison?: RegimeComparison;
  investment_recommendations: InvestmentRecommendation[];
  summary?: string; total_potential_savings: number; error?: string;
}

export interface ProgressState {
  stage: string; message: string; progress: number;
}

interface TaxStore {
  // Session
  sessionId: string | null;
  setSessionId: (id: string | null) => void;

  // Upload
  uploadedFile: File | null;
  setUploadedFile: (f: File | null) => void;
  riskProfile: RiskProfile;
  setRiskProfile: (r: RiskProfile) => void;

  // Analysis
  status: AnalysisStatus;
  setStatus: (s: AnalysisStatus) => void;
  progress: ProgressState;
  setProgress: (p: ProgressState) => void;
  result: AnalysisResult | null;
  setResult: (r: AnalysisResult | null) => void;

  // Chat
  chatMessages: { role: "user" | "assistant"; content: string }[];
  addChatMessage: (m: { role: "user" | "assistant"; content: string }) => void;
  clearChat: () => void;

  // Reset
  reset: () => void;
}

export const useTaxStore = create<TaxStore>((set) => ({
  sessionId: null,
  setSessionId: (id) => set({ sessionId: id }),

  uploadedFile: null,
  setUploadedFile: (f) => set({ uploadedFile: f }),
  riskProfile: "moderate",
  setRiskProfile: (r) => set({ riskProfile: r }),

  status: "idle",
  setStatus: (s) => set({ status: s }),
  progress: { stage: "", message: "", progress: 0 },
  setProgress: (p) => set({ progress: p }),
  result: null,
  setResult: (r) => set({ result: r }),

  chatMessages: [],
  addChatMessage: (m) => set((s) => ({ chatMessages: [...s.chatMessages, m] })),
  clearChat: () => set({ chatMessages: [] }),

  reset: () =>
    set({
      sessionId: null, uploadedFile: null, status: "idle",
      progress: { stage: "", message: "", progress: 0 },
      result: null, chatMessages: [],
    }),
}));
