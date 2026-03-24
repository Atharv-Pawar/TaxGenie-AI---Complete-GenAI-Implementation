"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Lock, DollarSign } from "lucide-react";

interface InvestmentRecommendationProps {
  investment: any;
  index: number;
}

export function InvestmentRecommendation({
  investment,
  index,
}: InvestmentRecommendationProps) {
  const riskColors = {
    low: "bg-green-500/20 border-green-500/30 text-green-200",
    medium: "bg-yellow-500/20 border-yellow-500/30 text-yellow-200",
    high: "bg-red-500/20 border-red-500/30 text-red-200",
  };

  const riskLevel = investment.risk_level?.toLowerCase() || "medium";

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className={`border ${riskColors[riskLevel as keyof typeof riskColors]}`}>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h3 className="font-semibold text-white text-lg mb-2">
                {investment.name}
              </h3>
              <p className="text-sm text-gray-300">{investment.description}</p>
            </div>
            <Badge variant="secondary" className="uppercase text-xs">
              {riskLevel} Risk
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Key Details Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-purple-400" />
              <div>
                <p className="text-xs text-gray-400">Returns</p>
                <p className="font-semibold text-white">{investment.returns}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-blue-400" />
              <div>
                <p className="text-xs text-gray-400">Lock-in</p>
                <p className="font-semibold text-white">{investment.lock_in}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-green-400" />
              <div>
                <p className="text-xs text-gray-400">Max Limit</p>
                <p className="font-semibold text-white">₹{investment.max_limit}</p>
              </div>
            </div>
          </div>

          {/* Features */}
          {investment.features && investment.features.length > 0 && (
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs font-medium text-white mb-2">Key Features:</p>
              <ul className="space-y-1">
                {investment.features.map((feature: string, idx: number) => (
                  <li key={idx} className="text-xs text-gray-400 flex gap-2">
                    <span className="text-purple-400">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Why Choose */}
          {investment.why_choose && (
            <div className="pt-3 border-t border-slate-700/50">
              <p className="text-sm font-medium text-white mb-2">Why choose this:</p>
              <p className="text-sm text-gray-400">{investment.why_choose}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}