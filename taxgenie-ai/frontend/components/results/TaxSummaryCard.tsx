"use client";
import { motion } from "framer-motion";
import { TrendingDown, Building2, Calendar } from "lucide-react";
import { formatINR } from "@/lib/utils";
import type { AnalysisResult } from "@/store/taxStore";

interface Props {
  result: AnalysisResult;
}

export default function TaxSummaryCard({ result }: Props) {
  const pd = result.parsed_data;
  const rc = result.regime_comparison;
  if (!pd || !rc) return null;

  const winnerTax =
    rc.recommended_regime === "NEW"
      ? rc.new_regime.total_tax
      : rc.old_regime.total_tax;

  const totalSavings = result.total_potential_savings;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl overflow-hidden border border-surface-border"
    >
      {/* Header banner */}
      <div className="bg-genie-gradient p-6 text-white">
        <p className="text-sm font-medium opacity-90 mb-1">Total Tax Savings Available</p>
        <p className="text-5xl font-extrabold tracking-tight">
          {formatINR(totalSavings)}
        </p>
        <p className="text-sm mt-2 opacity-80">
          Switch regime + claim missing deductions + invest wisely
        </p>
      </div>

      {/* Stats row */}
      <div className="bg-surface-card grid grid-cols-3 divide-x divide-surface-border">
        <Stat
          icon={<Building2 className="w-4 h-4" />}
          label="Employer"
          value={pd.employer_name ?? "—"}
          small
        />
        <Stat
          icon={<TrendingDown className="w-4 h-4" />}
          label="Optimised Tax"
          value={formatINR(winnerTax)}
        />
        <Stat
          icon={<Calendar className="w-4 h-4" />}
          label="Assessment Year"
          value={pd.assessment_year}
        />
      </div>
    </motion.div>
  );
}

function Stat({
  icon, label, value, small,
}: {
  icon: React.ReactNode; label: string; value: string; small?: boolean;
}) {
  return (
    <div className="p-4 flex flex-col gap-1">
      <span className="flex items-center gap-1.5 text-xs text-slate-500">
        {icon} {label}
      </span>
      <span className={`font-bold truncate ${small ? "text-sm text-slate-300" : "text-lg text-white"}`}>
        {value}
      </span>
    </div>
  );
}
