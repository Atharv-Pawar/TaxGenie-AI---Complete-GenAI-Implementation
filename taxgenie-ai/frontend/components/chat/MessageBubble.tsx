"use client";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface Props {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  followUps?: string[];
  onFollowUp?: (q: string) => void;
}

export default function MessageBubble({
  role, content, sources, followUps, onFollowUp,
}: Props) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 mt-0.5",
          isUser
            ? "bg-brand-500/20 text-brand-400"
            : "bg-surface-elevated text-slate-300"
        )}
      >
        {isUser ? "U" : "🧞"}
      </div>

      <div className={cn("flex flex-col gap-2 max-w-[80%]", isUser ? "items-end" : "items-start")}>
        {/* Bubble */}
        <div
          className={cn(
            "px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap",
            isUser
              ? "bg-brand-500 text-white rounded-tr-sm"
              : "bg-surface-card border border-surface-border text-slate-200 rounded-tl-sm"
          )}
        >
          {content}
        </div>

        {/* Sources */}
        {!isUser && sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {sources.map((s, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded-full bg-surface-elevated text-slate-500 text-xs"
              >
                📖 {s}
              </span>
            ))}
          </div>
        )}

        {/* Follow-up suggestions */}
        {!isUser && followUps && followUps.length > 0 && onFollowUp && (
          <div className="flex flex-col gap-1.5 w-full">
            {followUps.map((q, i) => (
              <button
                key={i}
                onClick={() => onFollowUp(q)}
                className="text-left px-3 py-2 rounded-xl bg-surface text-slate-400 hover:text-white hover:bg-surface-elevated text-xs border border-surface-border hover:border-brand-500/30 transition-all"
              >
                ↗ {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
