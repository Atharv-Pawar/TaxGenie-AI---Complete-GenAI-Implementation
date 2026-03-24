"use client";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  onFile: (file: File) => void;
  file: File | null;
  onClear: () => void;
  disabled?: boolean;
}

export default function FileDropzone({ onFile, file, onClear, disabled }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFile(accepted[0]);
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    disabled,
  });

  if (file) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex items-center gap-4 p-5 bg-green-500/10 border border-green-500/30 rounded-2xl"
      >
        <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
          <CheckCircle2 className="w-6 h-6 text-green-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-green-300 truncate">{file.name}</p>
          <p className="text-sm text-slate-500">
            {(file.size / 1024).toFixed(0)} KB · PDF
          </p>
        </div>
        {!disabled && (
          <button
            onClick={(e) => { e.stopPropagation(); onClear(); }}
            className="w-8 h-8 rounded-full bg-surface-card hover:bg-red-500/20 flex items-center justify-center text-slate-400 hover:text-red-400 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </motion.div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200",
        isDragActive
          ? "border-brand-500 bg-brand-500/10"
          : "border-surface-border hover:border-brand-500/50 hover:bg-surface-card",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <input {...getInputProps()} />
      <AnimatePresence mode="wait">
        {isDragActive ? (
          <motion.div
            key="drag"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
          >
            <Upload className="w-12 h-12 text-brand-400 mx-auto mb-3" />
            <p className="text-brand-400 font-semibold">Drop your Form 16 here</p>
          </motion.div>
        ) : (
          <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-300 font-semibold mb-1">
              Drag & drop your Form 16 PDF
            </p>
            <p className="text-sm text-slate-500 mb-4">or click to browse</p>
            <span className="inline-block px-4 py-2 bg-brand-500/10 border border-brand-500/20 rounded-lg text-brand-400 text-sm">
              Select PDF File
            </span>
            <p className="mt-4 text-xs text-slate-600">
              Supports Form 16 · Max 10MB · Your data is never stored permanently
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
