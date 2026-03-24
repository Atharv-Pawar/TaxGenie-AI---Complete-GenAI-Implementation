"use client";
import { motion } from "framer-motion";
import { CheckCircle2, Trophy } from "lucide-react";
import { formatINR } from "@/lib/utils";
import type { RegimeComparison as RC } from "@/store/taxStore";

interface Props { regime: RC; }

export default function RegimeComparison({ regime }: Props) {
  const { old_regime: old, new_regime: nw, recommended_regime: rec } = regime;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-surface-card border border-surface-border rounded-2xl overflow-hidden"
    >
      <div className="p-5 border-b border-surface-border flex items-center gap-2">
        <Trophy className="w-5 h-5 text-brand-400" />
        <h2 className="font-bold text-lg">Old vs New Regime</h2>
      </div>

      <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-surface-border">
        <RegimeColumn
          label="Old Regime"
          data={old}
          recommended={rec === "OLD"}
        />
        <RegimeColumn
          label="New Regime"
          data={nw}
          recommended={rec === "NEW"}
        />
      </div>

      {/* Recommendation */}
      <div className="p-5 bg-brand-500/5 border-t border-brand-500/20">
        <p className="text-sm text-slate-300 leading-relaxed">
          <span className="font-semibold text-brand-400">
            Recommendation:{" "}
          </span>
          {regime.recommendation_reason}
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Breakeven: If your total deductions reach{" "}
          <span className="text-slate-300 font-medium">
            {formatINR(regime.breakeven_deduction_amount)}
          </span>
          , Old Regime becomes better.
        </p>
      </div>
    </motion.div>
  );
}

function RegimeColumn({
  label, data, recommended,
}: {
  label: string;
  data: RC["old_regime"];
  recommended: boolean;
}) {
  const rows = [
    { label: "Gross Income",       value: data.gross_income },
    { label: "Total Deductions",   value: data.total_deductions },
    { label: "Taxable Income",     value: data.taxable_income },
    { label: "Tax (before cess)",  value: data.tax_before_cess },
    { label: "Health & Ed. Cess",  value: data.health_education_cess },
  ];

  return (
    <div className={`p-5 ${recommended ? "bg-green-500/5" : ""}`}>
      {/* Column header */}
      <div className="flex items-center justify-between mb-4">
        <span className="font-semibold">{label}</span>
        {recommended && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/15 border border-green-500/25 text-green-400 text-xs font-semibold">
            <CheckCircle2 className="w-3 h-3" /> RECOMMENDED
          </span>
        )}
      </div>

      {/* Breakdown rows */}
      <div className="space-y-2 mb-4">
        {rows.map((r) => (
          <div key={r.label} className="flex justify-between text-sm">
            <span className="text-slate-500">{r.label}</span>
            <span className="text-slate-200 font-medium tabular-nums">
              {formatINR(r.value)}
            </span>
          </div>
        ))}
      </div>

      {/* Total tax */}
      <div
        className={`flex justify-between items-center pt-3 border-t ${
          recommended ? "border-green-500/20" : "border-surface-border"
        }`}
      >
        <span className="font-bold">Total Tax</span>
        <span
          className={`text-xl font-extrabold tabular-nums ${
            recommended ? "text-green-400" : "text-slate-300"
          }`}
        >
          {formatINR(data.total_tax)}
        </span>
      </div>
    </div>
  );
}
