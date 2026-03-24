"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Loader2 } from "lucide-react";
import MessageBubble from "./MessageBubble";
import { sendChat } from "@/lib/api";
import { useTaxStore } from "@/store/taxStore";

const STARTER_QUESTIONS = [
  "Which tax regime is better for me?",
  "What investments can reduce my tax?",
  "How do I claim HRA exemption?",
  "What is Section 80C?",
  "Should I invest in ELSS or PPF?",
];

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  followUps?: string[];
}

export default function ChatInterface() {
  const sessionId = useTaxStore((s) => s.sessionId);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Namaste! 🧞 I'm TaxGenie, your personal tax advisor. Ask me anything about your taxes, deductions, or the Old vs New Regime. If you've uploaded your Form 16, I'll give you personalised answers!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const sid = sessionId ?? "anonymous";
      const res = await sendChat(sid, text);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.response,
          sources: res.sources,
          followUps: res.follow_up_suggestions,
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the server. Please check if the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            role={msg.role}
            content={msg.content}
            sources={msg.sources}
            followUps={msg.followUps}
            onFollowUp={send}
          />
        ))}

        {/* Loading indicator */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 rounded-full bg-surface-elevated flex items-center justify-center text-sm">
                🧞
              </div>
              <div className="px-4 py-3 bg-surface-card border border-surface-border rounded-2xl rounded-tl-sm">
                <div className="flex gap-1 items-center">
                  {[0, 1, 2].map((i) => (
                    <motion.span
                      key={i}
                      className="w-1.5 h-1.5 bg-brand-400 rounded-full"
                      animate={{ y: [0, -4, 0] }}
                      transition={{ repeat: Infinity, duration: 0.8, delay: i * 0.15 }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Starter questions (only if no user messages yet) */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-slate-600 mb-2">Suggested questions</p>
          <div className="flex flex-wrap gap-2">
            {STARTER_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="px-3 py-1.5 rounded-xl bg-surface-card border border-surface-border text-slate-400 hover:text-white hover:border-brand-500/30 text-xs transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input bar */}
      <div className="p-4 border-t border-surface-border">
        <form
          onSubmit={(e) => { e.preventDefault(); send(input); }}
          className="flex gap-2"
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask TaxGenie anything about your taxes…"
            className="flex-1 px-4 py-3 rounded-xl bg-surface-card border border-surface-border text-slate-200 placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/50 transition-colors"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="w-11 h-11 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center text-white transition-colors"
          >
            {loading
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <Send className="w-4 h-4" />}
          </button>
        </form>
      </div>
    </div>
  );
}
