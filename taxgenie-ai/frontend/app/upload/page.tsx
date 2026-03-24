"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, IndianRupee } from "lucide-react";
import Navbar from "@/components/shared/Navbar";
import FileDropzone from "@/components/upload/FileDropzone";
import LoadingOrchestrator from "@/components/shared/LoadingOrchestrator";
import { useTaxStore } from "@/store/taxStore";
import { uploadPDF, analyzeSync, createProgressSocket } from "@/lib/api";

const RISK_OPTIONS = [
  { value: "conservative", label: "Conservative", desc: "FD, PPF, NSC — capital safety first" },
  { value: "moderate",     label: "Moderate",     desc: "Mix of ELSS + PPF + NPS" },
  { value: "aggressive",   label: "Aggressive",   desc: "Mostly ELSS for max returns" },
] as const;

export default function UploadPage() {
  const router = useRouter();
  const {
    uploadedFile, setUploadedFile,
    riskProfile, setRiskProfile,
    status, setStatus,
    progress, setProgress,
    setSessionId, setResult,
  } = useTaxStore();

  const [manualIncome, setManualIncome] = useState("");
  const [error, setError] = useState<string | null>(null);

  const isProcessing = status === "uploading" || status === "processing";

  const handleAnalyse = async () => {
    if (!uploadedFile && !manualIncome) {
      setError("Please upload your Form 16 or enter your income manually.");
      return;
    }
    setError(null);

    try {
      // 1. Upload PDF
      setStatus("uploading");
      setProgress({ stage: "parsing", message: "Uploading your Form 16…", progress: 5 });

      let sessionId = "manual-" + Date.now();

      if (uploadedFile) {
        const uploadRes = await uploadPDF(uploadedFile);
        sessionId = uploadRes.session_id;
      } else {
        // No file — create a placeholder session via analyze directly
        const { default: axios } = await import("axios");
        const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const form = new FormData();
        // We'll pass manual income directly to analyze
        sessionId = "manual-" + Date.now();
        // Save a dummy session
        await axios.post(`${BASE}/api/v1/upload`, (() => {
          const f = new FormData();
          // Create a minimal PDF-like blob
          const blob = new Blob(["%PDF-1.4 minimal"], { type: "application/pdf" });
          f.append("file", blob, "manual.pdf");
          return f;
        })());
      }

      setSessionId(sessionId);

      // 2. Connect WebSocket for progress
      setStatus("processing");
      const ws = createProgressSocket(sessionId, (data) => {
        setProgress({ stage: data.stage, message: data.message, progress: data.progress });
      });

      // 3. Run analysis (sync for simplicity)
      setProgress({ stage: "parsing", message: "🔄 Parsing your Form 16…", progress: 15 });

      const result = await analyzeSync({
        session_id: sessionId,
        risk_profile: riskProfile,
        manual_income: manualIncome ? parseFloat(manualIncome) : undefined,
      });

      ws.close();

      setProgress({ stage: "done", message: "✅ Report ready!", progress: 100 });
      setResult(result);
      setStatus("completed");

      // Navigate to results
      setTimeout(() => router.push(`/results/${sessionId}`), 600);

    } catch (err: any) {
      setStatus("failed");
      setError(err?.response?.data?.detail ?? err?.message ?? "Analysis failed. Is the backend running?");
    }
  };

  return (
    <div className="min-h-screen bg-surface">
      <Navbar />

      <div className="max-w-2xl mx-auto px-4 pt-28 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          {/* Header */}
          <div>
            <h1 className="text-3xl font-extrabold mb-2">
              Analyse My Taxes <span className="genie-text">🧞</span>
            </h1>
            <p className="text-slate-400">
              Upload your Form 16 and get a personalised tax plan in under 90 seconds.
            </p>
          </div>

          {/* Processing overlay */}
          {isProcessing ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="py-12"
            >
              <LoadingOrchestrator
                stage={progress.stage}
                message={progress.message}
                progress={progress.progress}
              />
            </motion.div>
          ) : (
            <>
              {/* Step 1: Upload */}
              <div className="bg-surface-card border border-surface-border rounded-2xl p-6 space-y-4">
                <h2 className="font-semibold text-slate-300">
                  Step 1 — Upload Form 16
                </h2>
                <FileDropzone
                  onFile={setUploadedFile}
                  file={uploadedFile}
                  onClear={() => setUploadedFile(null)}
                  disabled={isProcessing}
                />

                <div className="flex items-center gap-3 text-slate-500 text-sm">
                  <div className="flex-1 h-px bg-surface-border" />
                  or enter income manually
                  <div className="flex-1 h-px bg-surface-border" />
                </div>

                <div className="relative">
                  <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="number"
                    value={manualIncome}
                    onChange={(e) => setManualIncome(e.target.value)}
                    placeholder="Annual gross salary (e.g. 1200000)"
                    className="w-full pl-9 pr-4 py-3 rounded-xl bg-surface border border-surface-border text-slate-200 placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/50 transition-colors"
                    disabled={isProcessing}
                  />
                </div>
              </div>

              {/* Step 2: Risk profile */}
              <div className="bg-surface-card border border-surface-border rounded-2xl p-6 space-y-3">
                <h2 className="font-semibold text-slate-300">
                  Step 2 — Investment Risk Profile
                </h2>
                <div className="grid grid-cols-3 gap-3">
                  {RISK_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setRiskProfile(opt.value)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        riskProfile === opt.value
                          ? "border-brand-500 bg-brand-500/10 text-white"
                          : "border-surface-border bg-surface text-slate-400 hover:border-brand-500/30"
                      }`}
                    >
                      <div className="font-semibold text-sm mb-0.5">{opt.label}</div>
                      <div className="text-xs opacity-70 leading-tight">{opt.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Error */}
              {error && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                >
                  ⚠️ {error}
                </motion.p>
              )}

              {/* CTA */}
              <button
                onClick={handleAnalyse}
                disabled={isProcessing || (!uploadedFile && !manualIncome)}
                className="w-full py-4 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold text-lg flex items-center justify-center gap-2 transition-colors"
              >
                Analyse Now <ArrowRight className="w-5 h-5" />
              </button>

              <p className="text-center text-xs text-slate-600">
                Your data is processed in-memory only and never stored permanently.
              </p>
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
}
