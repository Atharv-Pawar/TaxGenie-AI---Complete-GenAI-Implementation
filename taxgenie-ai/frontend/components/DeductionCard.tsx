"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronDown } from "lucide-react";
import { useState } from "react";

interface DeductionCardProps {
  deduction: any;
  index: number;
}

export function DeductionCard({ deduction, index }: DeductionCardProps) {
  const [expanded, setExpanded] = useState(false);

  const priorityColors = {
    HIGH: "bg-red-500/20 border-red-500/30 text-red-200",
    MEDIUM: "bg-yellow-500/20 border-yellow-500/30 text-yellow-200",
    LOW: "bg-blue-500/20 border-blue-500/30 text-blue-200",
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card
        className={`border cursor-pointer hover:border-purple-500/50 transition-all ${
          priorityColors[deduction.priority as keyof typeof priorityColors]
        }`}
        onClick={() => setExpanded(!expanded)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-2">{deduction.description}</h3>
              <p className="text-xs text-gray-400">{deduction.section}</p>
            </div>
            <Badge variant="secondary">{deduction.priority}</Badge>
          </div>
        </CardHeader>

        <motion.div
          initial={false}
          animate={{ height: expanded ? "auto" : 0, opacity: expanded ? 1 : 0 }}
          transition={{ duration: 0.3 }}
          className="overflow-hidden"
        >
          <CardContent className="space-y-4 pt-0">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-400 mb-1">Current</p>
                <p className="text-lg font-semibold text-white">
                  ₹{deduction.current_claimed.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Max Limit</p>
                <p className="text-lg font-semibold text-white">
                  ₹{deduction.max_limit.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Potential Saving</p>
                <p className="text-lg font-semibold text-green-400">
                  ₹{deduction.potential_tax_saving.toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-sm font-medium text-white mb-3">How to Claim:</p>
              <ul className="space-y-2">
                {deduction.how_to_claim.map((step: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-purple-400">{idx + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </motion.div>

        <div className="px-6 py-2 flex items-center justify-between">
          <span className="text-sm font-semibold text-white">
            Unused: ₹{deduction.unused_limit.toLocaleString('en-IN')}
          </span>
          <ChevronDown
            className={`w-4 h-4 transition-transform ${expanded ? "rotate-180" : ""}`}
          />
        </div>
      </Card>
    </motion.div>
  );
}