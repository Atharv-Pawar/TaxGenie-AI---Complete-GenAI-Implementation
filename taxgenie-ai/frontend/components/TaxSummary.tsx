"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";

export function TaxSummary({ data }: { data: any }) {
  const grossSalary = data.tax_data?.gross_salary || 0;
  const potentialSavings = data.missed_deductions?.reduce(
    (sum: number, d: any) => sum + (d.potential_tax_saving || 0),
    0
  ) || 0;
  const recommendation = data.regime_comparison?.recommendation?.regime || "N/A";
  const savings = data.regime_comparison?.comparison?.savings_amount || 0;

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="space-y-6">
      {/* Main Summary Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Gross Salary */}
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0 }}
        >
          <Card className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/30">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-400">
                Gross Salary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                ₹{(grossSalary / 100000).toFixed(2)}L
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Annual income before deductions
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Potential Savings */}
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-gradient-to-br from-green-500/10 to-green-500/5 border-green-500/30">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-400">
                Potential Tax Savings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">
                ₹{potentialSavings.toLocaleString('en-IN')}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                From missed deductions
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recommendation */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
      >
        <Card className="bg-purple-500/10 border-purple-500/30">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Tax Regime Recommendation</CardTitle>
              <Badge variant="default">
                {recommendation === "OLD" ? "Old Regime" : "New Regime"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-400 mb-2">Old Regime Tax</p>
                <p className="text-2xl font-bold">
                  ₹{data.regime_comparison?.old_regime_tax?.toLocaleString('en-IN') || "0"}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-2">New Regime Tax</p>
                <p className="text-2xl font-bold">
                  ₹{data.regime_comparison?.new_regime_tax?.toLocaleString('en-IN') || "0"}
                </p>
              </div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                {savings > 0 ? (
                  <TrendingDown className="w-4 h-4 text-green-400" />
                ) : (
                  <TrendingUp className="w-4 h-4 text-gray-400" />
                )}
                <span className="text-sm font-medium">
                  {recommendation} saves ₹{Math.abs(savings).toLocaleString('en-IN')}
                </span>
              </div>
              <p className="text-xs text-gray-400">
                {data.regime_comparison?.recommendation?.detailed_reasoning?.[0] ||
                  "Compare both regimes to optimize your tax liability"}
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Key Highlights */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
      >
        <Card className="bg-slate-700/50 border-slate-600">
          <CardHeader>
            <CardTitle>Key Highlights</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <span className="text-purple-400 font-bold">✓</span>
                <span className="text-gray-300">
                  You have <strong>{data.missed_deductions?.length || 0}</strong> missed deduction opportunities
                </span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-purple-400 font-bold">✓</span>
                <span className="text-gray-300">
                  Recommended regime: <strong>{recommendation}</strong>
                </span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-purple-400 font-bold">✓</span>
                <span className="text-gray-300">
                  Total potential savings: <strong>₹{potentialSavings.toLocaleString('en-IN')}</strong>
                </span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}