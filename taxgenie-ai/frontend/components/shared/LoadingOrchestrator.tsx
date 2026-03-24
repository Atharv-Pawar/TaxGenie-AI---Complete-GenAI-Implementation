"use client";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Loader2 } from "lucide-react";

const STAGES = [
  { key: "parsing",     label: "Parsing your Form 16",          emoji: "🔄" },
  { key: "analyzing",   label: "Finding missed deductions",      emoji: "🔍" },
  { key: "calculating", label: "Comparing tax regimes",          emoji: "⚖️" },
  { key: "recommending",label: "Building your investment plan",  emoji: "📈" },
  { key: "done",        label: "Report ready!",                  emoji: "✅" },
];

interface Props {
  stage: string;
  message: string;
  progress: number;
}

export default function LoadingOrchestrator({ stage, message, progress }: Props) {
  const currentIdx = STAGES.findIndex((s) => s.key === stage);

  return (
    <div className="w-full max-w-lg mx-auto">
      {/* Progress bar */}
      <div className="h-2 bg-surface-elevated rounded-full overflow-hidden mb-8">
        <motion.div
          className="h-full bg-genie-gradient rounded-full"
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>

      {/* Current message */}
      <AnimatePresence mode="wait">
        <motion.p
          key={message}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="text-center text-brand-400 font-medium mb-8"
        >
          {message}
        </motion.p>
      </AnimatePresence>

      {/* Stage checklist */}
      <div className="space-y-3">
        {STAGES.map((s, idx) => {
          const done    = idx < currentIdx || stage === "done";
          const active  = idx === currentIdx && stage !== "done";
          const pending = idx > currentIdx;

          return (
            <motion.div
              key={s.key}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: pending ? 0.3 : 1, x: 0 }}
              transition={{ delay: idx * 0.08 }}
              className="flex items-center gap-3"
            >
              <div className="w-7 h-7 flex items-center justify-center flex-shrink-0">
                {done ? (
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                ) : active ? (
                  <Loader2 className="w-5 h-5 text-brand-400 animate-spin" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-surface-border" />
                )}
              </div>
              <span
                className={
                  done    ? "text-slate-300 line-through decoration-slate-600" :
                  active  ? "text-white font-medium" :
                  "text-slate-600"
                }
              >
                {s.emoji} {s.label}
              </span>
              {active && (
                <span className="ml-auto text-xs text-brand-400 animate-pulse">
                  {progress}%
                </span>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
