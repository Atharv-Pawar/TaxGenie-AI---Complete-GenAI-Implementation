"use client";
import { motion } from "framer-motion";
import { TrendingUp, Lock, ShieldCheck } from "lucide-react";
import { formatINR } from "@/lib/utils";
import type { InvestmentRecommendation } from "@/store/taxStore";

interface Props { recommendations: InvestmentRecommendation[]; }

const riskColor: Record<string, string> = {
  Low: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  Moderate: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
  "Moderate-High": "text-orange-400 bg-orange-500/10 border-orange-500/20",
  High: "text-red-400 bg-red-500/10 border-red-500/20",
};

export default function InvestmentPlan({ recommendations }: Props) {
  if (!recommendations.length) return null;

  const totalInvest = recommendations.reduce(
    (s, r) => s + r.recommended_amount, 0
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-surface-card border border-surface-border rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <div className="p-5 border-b border-surface-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-brand-400" />
          <h2 className="font-bold text-lg">Investment Plan</h2>
        </div>
        <p className="text-sm text-slate-500">
          Total: <span className="text-white font-semibold">{formatINR(totalInvest)}</span>
        </p>
      </div>

      {/* Cards */}
      <div className="p-5 grid gap-4">
        {recommendations.map((rec, idx) => {
          const riskClass = riskColor[rec.risk_level] ?? riskColor.Moderate;
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.06 * idx }}
              className="p-4 bg-surface rounded-xl border border-surface-border card-glow"
            >
              {/* Top row */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-0.5">
                    <span className="font-semibold">{rec.instrument}</span>
                    <span className="px-2 py-0.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs">
                      {rec.section}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400">{rec.reason}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs text-slate-500">Invest</p>
                  <p className="text-lg font-extrabold text-white tabular-nums">
                    {formatINR(rec.recommended_amount)}
                  </p>
                </div>
              </div>

              {/* Meta row */}
              <div className="flex items-center gap-3 flex-wrap text-xs">
                <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full border ${riskClass}`}>
                  <ShieldCheck className="w-3 h-3" />
                  {rec.risk_level} Risk
                </span>
                <span className="flex items-center gap-1 text-slate-500">
                  <TrendingUp className="w-3 h-3" />
                  {rec.expected_returns}
                </span>
                <span className="flex items-center gap-1 text-slate-500">
                  <Lock className="w-3 h-3" />
                  {rec.lock_in_period}
                </span>
              </div>

              {/* Top picks */}
              {rec.top_picks?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-surface-border">
                  <p className="text-xs text-slate-600 mb-1.5">Top picks</p>
                  <div className="flex flex-wrap gap-1.5">
                    {rec.top_picks.map((pick, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded-md bg-surface-elevated text-slate-400 text-xs"
                      >
                        {pick}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
