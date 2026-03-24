"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Upload, MessageCircle, TrendingUp, IndianRupee,
  ArrowRight, FileText, AlertCircle,
} from "lucide-react";
import Navbar from "@/components/shared/Navbar";
import { useTaxStore } from "@/store/taxStore";
import { formatINR } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";

export default function DashboardPage() {
  const { result, sessionId } = useTaxStore();

  if (!result || !result.parsed_data) {
    return (
      <div className="min-h-screen bg-surface">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 pt-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="text-6xl">🧞</div>
            <h1 className="text-2xl font-bold">No Analysis Yet</h1>
            <p className="text-slate-400">
              Upload your Form 16 to get your personalised tax dashboard.
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-8 py-4 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl transition-colors"
            >
              <Upload className="w-5 h-5" /> Analyse My Taxes
            </Link>
          </motion.div>
        </div>
      </div>
    );
  }

  const pd = result.parsed_data;
  const rc = result.regime_comparison!;
  const md = result.missed_deductions;

  const chartData = [
    { name: "Old Regime", tax: rc.old_regime.total_tax, fill: "#64748b" },
    { name: "New Regime", tax: rc.new_regime.total_tax, fill: "#f97316" },
  ];

  const topMissed = md?.missed_deductions?.slice(0, 3) ?? [];

  return (
    <div className="min-h-screen bg-surface">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 pt-24 pb-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-end justify-between"
        >
          <div>
            <h1 className="text-3xl font-extrabold">Tax Dashboard</h1>
            <p className="text-slate-400 mt-1">
              {pd.employer_name} · AY {pd.assessment_year}
            </p>
          </div>
          <Link
            href={`/results/${sessionId}`}
            className="text-sm text-brand-400 hover:text-brand-300 flex items-center gap-1"
          >
            Full Report <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>

        {/* KPI cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Gross Salary",       value: formatINR(pd.gross_salary),              icon: <IndianRupee className="w-4 h-4" />, color: "text-white" },
            { label: "TDS Paid",           value: formatINR(pd.total_tds_deducted),         icon: <FileText className="w-4 h-4" />,   color: "text-slate-300" },
            { label: "Regime Savings",     value: formatINR(rc.savings_with_recommended),   icon: <TrendingUp className="w-4 h-4" />, color: "text-green-400" },
            { label: "Total Opportunity",  value: formatINR(result.total_potential_savings), icon: <AlertCircle className="w-4 h-4" />,color: "text-brand-400" },
          ].map((kpi, i) => (
            <motion.div
              key={kpi.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="bg-surface-card border border-surface-border rounded-2xl p-4"
            >
              <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-2">
                {kpi.icon} {kpi.label}
              </div>
              <div className={`text-xl font-extrabold tabular-nums ${kpi.color}`}>
                {kpi.value}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Main grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Regime chart */}
          <motion.div
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-surface-card border border-surface-border rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold">Regime Comparison</h2>
              <span className="text-xs px-2 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400">
                {rc.recommended_regime} wins
              </span>
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={chartData} barSize={48}>
                <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis hide />
                <Tooltip
                  formatter={(v: number) => formatINR(v)}
                  contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
                />
                <Bar dataKey="tax" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={index} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-slate-500 mt-2 text-center">
              Save {formatINR(rc.savings_with_recommended)} by choosing {rc.recommended_regime} Regime
            </p>
          </motion.div>

          {/* Top missed deductions */}
          <motion.div
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }}
            className="bg-surface-card border border-surface-border rounded-2xl p-5"
          >
            <h2 className="font-bold mb-4">Top Missed Deductions</h2>
            {topMissed.length === 0 ? (
              <p className="text-slate-500 text-sm">No missed deductions found 🎉</p>
            ) : (
              <div className="space-y-3">
                {topMissed.map((d) => (
                  <div key={d.section} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Section {d.section}</p>
                      <p className="text-xs text-slate-500 truncate max-w-[200px]">{d.description.slice(0, 55)}…</p>
                    </div>
                    <span className="text-green-400 font-bold tabular-nums text-sm">
                      +{formatINR(d.potential_saving)}
                    </span>
                  </div>
                ))}
                <Link
                  href={`/results/${sessionId}`}
                  className="block text-center text-xs text-brand-400 hover:text-brand-300 mt-2"
                >
                  View all deductions →
                </Link>
              </div>
            )}
          </motion.div>
        </div>

        {/* Quick actions */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-6 grid grid-cols-3 gap-4"
        >
          <Link href={`/results/${sessionId}`} className="flex flex-col items-center gap-2 p-4 bg-surface-card border border-surface-border rounded-2xl hover:border-brand-500/30 transition-all text-center">
            <FileText className="w-6 h-6 text-brand-400" />
            <span className="text-sm font-medium">Full Report</span>
          </Link>
          <Link href="/chat" className="flex flex-col items-center gap-2 p-4 bg-surface-card border border-surface-border rounded-2xl hover:border-brand-500/30 transition-all text-center">
            <MessageCircle className="w-6 h-6 text-brand-400" />
            <span className="text-sm font-medium">Ask TaxGenie</span>
          </Link>
          <Link href="/upload" className="flex flex-col items-center gap-2 p-4 bg-surface-card border border-surface-border rounded-2xl hover:border-brand-500/30 transition-all text-center">
            <Upload className="w-6 h-6 text-brand-400" />
            <span className="text-sm font-medium">New Analysis</span>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
