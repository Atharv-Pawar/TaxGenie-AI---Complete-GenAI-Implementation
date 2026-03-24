"use client";
import Navbar from "@/components/shared/Navbar";
import ChatInterface from "@/components/chat/ChatInterface";
import { useTaxStore } from "@/store/taxStore";
import { formatINR } from "@/lib/utils";
import { motion } from "framer-motion";

export default function ChatPage() {
  const result = useTaxStore((s) => s.result);
  const pd = result?.parsed_data;
  const rc = result?.regime_comparison;

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <Navbar />

      <div className="flex-1 max-w-3xl w-full mx-auto px-4 pt-20 pb-0 flex flex-col">
        {/* Context banner (if analysis available) */}
        {pd && rc && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 mb-2 px-4 py-2 bg-brand-500/5 border border-brand-500/20 rounded-xl text-xs text-slate-400 flex flex-wrap gap-3"
          >
            <span>💼 {pd.employer_name}</span>
            <span>💰 {formatINR(pd.gross_salary)}</span>
            <span>🏆 {rc.recommended_regime} Regime recommended</span>
            <span>📊 Saves {formatINR(rc.savings_with_recommended)}</span>
          </motion.div>
        )}

        {/* Chat interface fills remaining space */}
        <div className="flex-1 bg-surface-card border border-surface-border rounded-t-2xl overflow-hidden flex flex-col mt-2">
          <div className="px-5 py-4 border-b border-surface-border flex items-center gap-2">
            <span className="text-lg">🧞</span>
            <div>
              <p className="font-semibold text-sm">TaxGenie AI</p>
              <p className="text-xs text-slate-500">
                {pd ? "Using your Form 16 data for personalised answers" : "General tax Q&A mode"}
              </p>
            </div>
            <div className="ml-auto w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          </div>

          <div className="flex-1 overflow-hidden">
            <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}
