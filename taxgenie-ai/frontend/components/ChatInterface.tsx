"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Loader, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  error?: boolean;
}

interface ChatInterfaceProps {
  initialMessages?: Message[];
  onMessageSend?: (message: string) => void;
  isLoading?: boolean;
  context?: any;
}

const QUICK_QUESTIONS = [
  "What is Section 80C and which investments qualify?",
  "Should I choose old or new tax regime?",
  "How can I maximize my tax savings?",
  "What's the difference between 80C and 80CCD(1B)?",
  "Can I invest in multiple schemes for 80C?",
  "How does HRA exemption work?",
  "What investments give best returns for 80C?",
];

export function ChatInterface({
  initialMessages = [],
  onMessageSend,
  isLoading = false,
  context,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! 👋 I'm TaxGenie, your AI tax assistant. I can help you understand your tax analysis, explain deductions, and answer any questions about tax planning. What would you like to know?",
      timestamp: new Date(),
    },
    ...initialMessages,
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      // Call chat API
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          context: context ? JSON.stringify(context) : null,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response || "I couldn't process that request. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Call optional callback
      if (onMessageSend) {
        onMessageSend(input);
      }
    } catch (err) {
      console.error("Chat error:", err);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Sorry, I encountered an error. Please try again or rephrase your question.",
        timestamp: new Date(),
        error: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto space-y-4 p-6 bg-slate-800/50 rounded-lg border border-slate-700">
        <AnimatePresence mode="popLayout">
          {messages.map((msg, idx) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: idx * 0.02 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg break-words ${
                  msg.role === "user"
                    ? "bg-purple-600 text-white rounded-br-none"
                    : msg.error
                    ? "bg-red-500/20 text-red-200 border border-red-500/30 rounded-bl-none"
                    : "bg-slate-700 text-gray-100 rounded-bl-none"
                }`}
              >
                <p className="text-sm leading-relaxed">{msg.content}</p>
                <p className="text-xs mt-2 opacity-70">
                  {msg.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </motion.div>
          ))}

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 text-gray-400"
            >
              <Loader className="w-4 h-4 animate-spin" />
              <span className="text-sm">TaxGenie is thinking...</span>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Questions - Show on initial state */}
      {messages.length <= 1 && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="bg-slate-800/50 border border-slate-700 rounded-lg p-4"
        >
          <p className="text-xs text-gray-400 mb-3 font-medium">Quick Questions:</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-40 overflow-y-auto">
            {QUICK_QUESTIONS.map((q, idx) => (
              <motion.button
                key={idx}
                onClick={() => handleQuickQuestion(q)}
                className="text-left text-xs p-2 rounded border border-slate-600 hover:border-purple-500/50 
                         hover:bg-purple-500/10 transition-colors text-gray-300"
                whileHover={{ x: 2 }}
                disabled={loading}
              >
                {q}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-200 text-sm"
        >
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}

      {/* Input Area */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
            placeholder="Ask about taxes, deductions, investments..."
            disabled={loading}
            className="bg-slate-700 border-slate-600 text-white placeholder-gray-500 flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || loading}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 h-10"
          >
            {loading ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💡 Tip: Ask specific questions for detailed answers | Press Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}