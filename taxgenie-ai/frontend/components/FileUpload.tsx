"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileIcon, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FileUploadProps {
  onUpload: (file: File) => void;
  disabled?: boolean;
}

export function FileUpload({ onUpload, disabled = false }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === "application/pdf") {
        setSelectedFile(file);
        onUpload(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === "application/pdf") {
        setSelectedFile(file);
        onUpload(file);
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Upload Area */}
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        whileHover={{ scale: 1.02 }}
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
          isDragging
            ? "border-purple-500 bg-purple-500/10"
            : "border-slate-600 hover:border-purple-500/50"
        } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
      >
        <motion.div
          animate={{ scale: isDragging ? 1.1 : 1 }}
          className="text-5xl mb-4"
        >
          📄
        </motion.div>

        <h3 className="text-xl font-semibold text-white mb-2">
          Upload Your Form 16
        </h3>
        <p className="text-gray-400 mb-4">
          Drag and drop your PDF here or click to browse
        </p>

        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          disabled={disabled}
          className="hidden"
          id="file-input"
        />

        <label htmlFor="file-input">
          <Button
            asChild
            variant="secondary"
            className="cursor-pointer"
            disabled={disabled}
          >
            <span>
              <Upload className="w-4 h-4 mr-2" />
              Select File
            </span>
          </Button>
        </label>

        <p className="text-gray-500 text-sm mt-4">
          Maximum file size: 10MB | PDF format only
        </p>
      </motion.div>

      {/* Selected File Info */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 flex items-start gap-3"
        >
          <FileIcon className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-green-200 truncate">
              {selectedFile.name}
            </p>
            <p className="text-sm text-green-400">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        </motion.div>
      )}

      {/* Info Box */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 flex gap-3">
        <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-200">
          <p className="font-medium mb-2">We need your Form 16 which includes:</p>
          <ul className="space-y-1 text-xs">
            <li>✓ Gross salary and all components</li>
            <li>✓ All exemptions (HRA, LTA, etc.)</li>
            <li>✓ All deductions (80C, 80D, etc.)</li>
            <li>✓ TDS deducted amount</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
}