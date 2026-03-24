"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader, Download, Share2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TaxSummary } from "@/components/TaxSummary";
import { DeductionCard } from "@/components/DeductionCard";
import { RegimeComparison } from "@/components/RegimeComparison";
import { InvestmentRecommendation } from "@/components/InvestmentRecommendation";
import { useRouter } from "next/navigation";

interface AnalysisData {
  tax_data: any;
  missed_deductions: any[];
  regime_comparison: any;
  investment_recommendations: any[];
  summary: string;
  errors: string[];
}

export default function AnalysisPage() {
  const router = useRouter();
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("summary");

  useEffect(() => {
    const runAnalysis = async () => {
      try {
        const taxDataStr = sessionStorage.getItem("taxData");
        if (!taxDataStr) {
          setError("No tax data found. Please upload a Form 16 first.");
          setLoading(false);
          return;
        }

        const taxData = JSON.parse(taxDataStr);

        // Call backend analysis endpoint
        const response = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tax_data: taxData }),
        });

        if (!response.ok) throw new Error("Analysis failed");

        const data: AnalysisData = await response.json();
        setAnalysisData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Analysis failed");
      } finally {
        setLoading(false);
      }
    };

    runAnalysis();
  }, []);

  const handleDownloadReport = () => {
    // Generate PDF or download functionality
    const reportData = {
      timestamp: new Date().toISOString(),
      analysis: analysisData,
    };

    const element = document.createElement("a");
    element.href = "data:text/plain;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    element.download = `TaxGenie_Report_${Date.now()}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-6xl mb-4"
          >
            🧞‍♂️
          </motion.div>
          <Loader className="w-8 h-8 animate-spin mx-auto text-purple-400 mb-4" />
          <p className="text-gray-300">Analyzing your tax data with AI...</p>
          <p className="text-gray-500 text-sm mt-2">This may take a moment</p>
        </motion.div>
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <Card className="bg-red-500/10 border-red-500/30 p-8 max-w-md w-full">
          <div className="text-center">
            <div className="text-4xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-red-200 mb-2">Analysis Error</h2>
            <p className="text-gray-400 mb-6">{error || "Failed to complete analysis"}</p>
            <Button
              onClick={() => router.push("/upload")}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              Try Again
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Your Tax Analysis Report
          </h1>
          <p className="text-gray-400 text-lg">
            Here's your personalized tax optimization plan
          </p>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex gap-4 mb-8 flex-wrap"
        >
          <Button
            onClick={handleDownloadReport}
            variant="outline"
            className="border-purple-500/30 hover:bg-purple-500/10"
          >
            <Download className="w-4 h-4 mr-2" />
            Download Report
          </Button>
          <Button
            variant="outline"
            className="border-purple-500/30 hover:bg-purple-500/10"
          >
            <Share2 className="w-4 h-4 mr-2" />
            Share Results
          </Button>
        </motion.div>

        {/* Tab Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="grid w-full grid-cols-4 bg-slate-700/50 mb-8">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="deductions">Deductions</TabsTrigger>
            <TabsTrigger value="regime">Regime</TabsTrigger>
            <TabsTrigger value="investments">Investments</TabsTrigger>
          </TabsList>

          {/* Summary Tab */}
          <TabsContent value="summary">
            <AnimatePresence>
              <motion.div
                key="summary"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <TaxSummary data={analysisData} />
              </motion.div>
            </AnimatePresence>
          </TabsContent>

          {/* Deductions Tab */}
          <TabsContent value="deductions">
            <AnimatePresence>
              <motion.div
                key="deductions"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                {analysisData.missed_deductions && analysisData.missed_deductions.length > 0 ? (
                  analysisData.missed_deductions.map((deduction: any, idx: number) => (
                    <motion.div
                      key={deduction.section}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                    >
                      <DeductionCard deduction={deduction} index={idx} />
                    </motion.div>
                  ))
                ) : (
                  <Card className="bg-slate-800 border-slate-700 p-6 text-center">
                    <p className="text-gray-400">No additional deductions found at this time.</p>
                  </Card>
                )}
              </motion.div>
            </AnimatePresence>
          </TabsContent>

          {/* Regime Tab */}
          <TabsContent value="regime">
            <AnimatePresence>
              <motion.div
                key="regime"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <RegimeComparison data={analysisData.regime_comparison} />
              </motion.div>
            </AnimatePresence>
          </TabsContent>

          {/* Investments Tab */}
          <TabsContent value="investments">
            <AnimatePresence>
              <motion.div
                key="investments"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                {analysisData.investment_recommendations && analysisData.investment_recommendations.length > 0 ? (
                  analysisData.investment_recommendations.map((inv: any, idx: number) => (
                    <motion.div
                      key={inv.name}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                    >
                      <InvestmentRecommendation investment={inv} index={idx} />
                    </motion.div>
                  ))
                ) : (
                  <Card className="bg-slate-800 border-slate-700 p-6 text-center">
                    <p className="text-gray-400">Generating investment recommendations...</p>
                  </Card>
                )}
              </motion.div>
            </AnimatePresence>
          </TabsContent>
        </Tabs>

        {/* Chat CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-12 bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-lg p-8 text-center"
        >
          <h3 className="text-2xl font-bold mb-3">Have Questions?</h3>
          <p className="text-gray-400 mb-6">
            Chat with our AI Tax Assistant to clarify any details about your analysis
          </p>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              onClick={() => router.push("/chat")}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              Start Chat <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}