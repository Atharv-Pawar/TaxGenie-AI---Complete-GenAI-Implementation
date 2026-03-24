"use client";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

interface Props {
  progress: number;
  message: string;
}

export default function UploadProgress({ progress, message }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-3"
    >
      <div className="flex items-center justify-between text-sm">
        <span className="flex items-center gap-2 text-brand-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          {message}
        </span>
        <span className="text-slate-500 font-mono">{progress}%</span>
      </div>
      <div className="h-1.5 bg-surface-elevated rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-genie-gradient rounded-full"
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.35, ease: "easeOut" }}
        />
      </div>
    </motion.div>
  );
}
