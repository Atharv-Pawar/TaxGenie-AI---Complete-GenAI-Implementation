"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { MessageCircle, RefreshCw, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";
import Navbar from "@/components/shared/Navbar";
import TaxSummaryCard from "@/components/results/TaxSummaryCard";
import RegimeComparison from "@/components/results/RegimeComparison";
import DeductionList from "@/components/results/DeductionList";
import InvestmentPlan from "@/components/results/InvestmentPlan";
import { useTaxStore } from "@/store/taxStore";
import { getResults } from "@/lib/api";
import type { AnalysisResult } from "@/store/taxStore";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const storeResult = useTaxStore((s) => s.result);
  const setResult = useTaxStore((s) => s.setResult);
  const setSessionId = useTaxStore((s) => s.setSessionId);

  const [result, setLocalResult] = useState<AnalysisResult | null>(storeResult);
  const [loading, setLoading] = useState(!storeResult);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    setSessionId(sessionId);
    if (storeResult) return;

    const fetchResult = async () => {
      try {
        setLoading(true);
        const data = await getResults(sessionId);

        if (data.status === "processing") {
          // Poll every 2s
          setPolling(true);
          const interval = setInterval(async () => {
            const d = await getResults(sessionId);
            if (d.status !== "processing") {
              clearInterval(interval);
              setPolling(false);
              setLocalResult(d);
              setResult(d);
              setLoading(false);
            }
          }, 2000);
        } else {
          setLocalResult(data);
          setResult(data);
          setLoading(false);
        }
      } catch {
        setError("Could not load results. The session may have expired.");
        setLoading(false);
      }
    };

    fetchResult();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center flex-col gap-4">
          <Loader2 className="w-10 h-10 text-brand-400 animate-spin" />
          <p className="text-slate-400">
            {polling ? "Waiting for analysis to complete…" : "Loading your results…"}
          </p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-surface flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center flex-col gap-4">
          <AlertCircle className="w-10 h-10 text-red-400" />
          <p className="text-slate-400">{error ?? "Results not found."}</p>
          <Link href="/upload" className="px-6 py-3 rounded-xl bg-brand-500 text-white font-semibold text-sm">
            Try Again
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface">
      <Navbar />

      <div className="max-w-3xl mx-auto px-4 pt-24 pb-16 space-y-6">
        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-extrabold">Your Tax Analysis</h1>
            <p className="text-sm text-slate-500 mt-0.5">Session: {sessionId.slice(0, 8)}…</p>
          </div>
          <div className="flex gap-2">
            <Link
              href={`/chat`}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-surface-card border border-surface-border text-slate-300 hover:text-white hover:border-brand-500/30 text-sm font-medium transition-all"
            >
              <MessageCircle className="w-4 h-4" /> Ask Questions
            </Link>
            <Link
              href="/upload"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-surface-card border border-surface-border text-slate-300 hover:text-white text-sm transition-all"
            >
              <RefreshCw className="w-4 h-4" /> New Analysis
            </Link>
          </div>
        </motion.div>

        {/* AI Summary */}
        {result.summary && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-5 bg-brand-500/5 border border-brand-500/20 rounded-2xl"
          >
            <p className="text-xs text-brand-400 font-semibold uppercase tracking-wide mb-2">
              🧞 TaxGenie Summary
            </p>
            <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-line">
              {result.summary}
            </p>
          </motion.div>
        )}

        {/* Summary card */}
        {result.parsed_data && result.regime_comparison && (
          <TaxSummaryCard result={result} />
        )}

        {/* Regime comparison */}
        {result.regime_comparison && (
          <RegimeComparison regime={result.regime_comparison} />
        )}

        {/* Missed deductions */}
        {result.missed_deductions && (
          <DeductionList deductions={result.missed_deductions} />
        )}

        {/* Investment plan */}
        {result.investment_recommendations?.length > 0 && (
          <InvestmentPlan recommendations={result.investment_recommendations} />
        )}

        {/* Error state */}
        {result.error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
            ⚠️ {result.error}
          </div>
        )}

        {/* Chat CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center py-6"
        >
          <p className="text-slate-500 text-sm mb-3">
            Have questions about your results?
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-semibold transition-colors"
          >
            <MessageCircle className="w-4 h-4" />
            Chat with TaxGenie
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
