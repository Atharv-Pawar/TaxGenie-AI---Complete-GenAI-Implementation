"use client";
import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { formatINR, urgencyColor } from "@/lib/utils";
import type { DeductionResult } from "@/store/taxStore";

interface Props { deductions: DeductionResult; }

export default function DeductionList({ deductions }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-surface-card border border-surface-border rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <div className="p-5 border-b border-surface-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-yellow-400" />
          <h2 className="font-bold text-lg">Missed Deductions</h2>
        </div>
        <div className="px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-sm font-semibold">
          ₹{(deductions.total_potential_savings / 1000).toFixed(0)}K potential
        </div>
      </div>

      {/* Claimed (collapsed) */}
      {deductions.claimed_deductions.length > 0 && (
        <div className="px-5 py-3 border-b border-surface-border bg-green-500/5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Already Claimed</p>
          <div className="flex flex-wrap gap-2">
            {deductions.claimed_deductions.map((d, i) => (
              <span
                key={i}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-xs"
              >
                <CheckCircle2 className="w-3 h-3" />
                {d.section}: {formatINR(d.amount)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missed deductions */}
      <div className="divide-y divide-surface-border">
        {deductions.missed_deductions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            <CheckCircle2 className="w-8 h-8 text-green-400 mx-auto mb-2" />
            <p>Great news — no major missed deductions found!</p>
          </div>
        ) : (
          deductions.missed_deductions.map((d, idx) => {
            const isOpen = expanded === d.section;
            const colorClass = urgencyColor(d.urgency);
            return (
              <motion.div
                key={d.section}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * idx }}
              >
                <button
                  className="w-full text-left p-5 hover:bg-surface-elevated transition-colors"
                  onClick={() => setExpanded(isOpen ? null : d.section)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="font-semibold">Section {d.section}</span>
                        <span className={`px-2 py-0.5 rounded-full border text-xs font-medium ${colorClass}`}>
                          {d.urgency}
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 line-clamp-2">{d.description}</p>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <div className="text-right">
                        <p className="text-xs text-slate-500">Potential saving</p>
                        <p className="font-bold text-green-400 tabular-nums">
                          {formatINR(d.potential_saving)}
                        </p>
                      </div>
                      {isOpen
                        ? <ChevronUp className="w-4 h-4 text-slate-500" />
                        : <ChevronDown className="w-4 h-4 text-slate-500" />}
                    </div>
                  </div>
                </button>

                {/* Expanded suggestions */}
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="px-5 pb-4"
                  >
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                      Action Steps
                    </p>
                    <ul className="space-y-1.5">
                      {d.suggestions.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                          <span className="text-brand-400 mt-0.5">→</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                )}
              </motion.div>
            );
          })
        )}
      </div>
    </motion.div>
  );
}
