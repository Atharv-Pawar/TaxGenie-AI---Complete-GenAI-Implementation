"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingDown } from "lucide-react";

export function RegimeComparison({ data }: { data: any }) {
  const oldTax = data?.old_regime_tax || 0;
  const newTax = data?.new_regime_tax || 0;
  const recommended = data?.recommendation?.regime || "OLD";
  const savings = Math.abs(data?.comparison?.savings_amount || 0);

  const maxValue = Math.max(oldTax, newTax);
  const oldPercentage = (oldTax / maxValue) * 100;
  const newPercentage = (newTax / maxValue) * 100;

  return (
    <div className="space-y-6">
      {/* Comparison Charts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid md:grid-cols-2 gap-6"
      >
        {/* Old Regime */}
        <Card className="border-slate-700 bg-slate-800">
          <CardHeader>
            <CardTitle className="text-lg">Old Regime</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Tax Liability</span>
                <span className="text-2xl font-bold text-white">
                  ₹{oldTax.toLocaleString('en-IN')}
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${oldPercentage}%` }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                  className="h-full bg-gradient-to-r from-blue-600 to-blue-400"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6 pt-4 border-t border-slate-700">
              <div>
                <p className="text-xs text-gray-400">Base Tax</p>
                <p className="text-lg font-semibold">
                  ₹{(data?.old_regime?.tax_before_cess || 0).toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">+ Cess (4%)</p>
                <p className="text-lg font-semibold">
                  ₹{(data?.old_regime?.cess || 0).toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* New Regime */}
        <Card className="border-slate-700 bg-slate-800">
          <CardHeader>
            <CardTitle className="text-lg">New Regime</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Tax Liability</span>
                <span className="text-2xl font-bold text-white">
                  ₹{newTax.toLocaleString('en-IN')}
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${newPercentage}%` }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                  className="h-full bg-gradient-to-r from-green-600 to-green-400"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6 pt-4 border-t border-slate-700">
              <div>
                <p className="text-xs text-gray-400">Base Tax</p>
                <p className="text-lg font-semibold">
                  ₹{(data?.new_regime?.tax_before_cess || 0).toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">+ Cess (4%)</p>
                <p className="text-lg font-semibold">
                  ₹{(data?.new_regime?.cess || 0).toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommendation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="bg-gradient-to-br from-purple-500/20 to-purple-500/5 border-purple-500/50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recommendation</CardTitle>
              <Badge variant="default" className="text-lg">
                {recommended} Regime
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3 bg-slate-700/50 rounded-lg p-4">
              <TrendingDown className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold text-white mb-1">
                  Save ₹{savings.toLocaleString('en-IN')} annually
                </p>
                <p className="text-sm text-gray-400">
                  {data?.recommendation?.primary_reason || "Choose the regime that minimizes your tax liability"}
                </p>
              </div>
            </div>

            {data?.recommendation?.detailed_reasoning && (
              <div className="space-y-2 pt-4 border-t border-slate-700">
                <p className="text-sm font-medium text-white mb-3">Why this regime:</p>
                {data.recommendation.detailed_reasoning.map((reason: string, idx: number) => (
                  <p key={idx} className="text-sm text-gray-400 flex gap-2">
                    <span className="text-purple-400">•</span>
                    <span>{reason}</span>
                  </p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}