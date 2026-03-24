"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Upload, AlertCircle, CheckCircle, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { FileUpload } from "@/components/FileUpload";
import { ManualInput } from "@/components/ManualInput";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface UploadState {
  status: "idle" | "uploading" | "success" | "error";
  message: string;
  file?: File;
}

export default function UploadPage() {
  const router = useRouter();
  const [uploadState, setUploadState] = useState<UploadState>({ status: "idle", message: "" });
  const [activeTab, setActiveTab] = useState<"upload" | "manual">("upload");

  const handleFileUpload = async (file: File) => {
    setUploadState({ status: "uploading", message: "Uploading and parsing your Form 16..." });

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");

      const data = await response.json();
      
      setUploadState({
        status: "success",
        message: "Form 16 uploaded successfully!",
        file: file,
      });

      // Store tax data in sessionStorage for analysis page
      sessionStorage.setItem("taxData", JSON.stringify(data.extracted_data));

      // Redirect after 2 seconds
      setTimeout(() => {
        router.push("/analysis");
      }, 2000);
    } catch (error) {
      setUploadState({
        status: "error",
        message: "Failed to upload file. Please try again.",
      });
    }
  };

  const handleManualSubmit = (data: any) => {
    setUploadState({ status: "uploading", message: "Processing your data..." });

    setTimeout(() => {
      setUploadState({
        status: "success",
        message: "Data submitted successfully!",
      });

      // Store tax data
      sessionStorage.setItem("taxData", JSON.stringify(data));

      setTimeout(() => {
        router.push("/analysis");
      }, 2000);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-20">
      <div className="container mx-auto px-4">
        <motion.div
          className="max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Upload Your <span className="text-purple-400">Form 16</span>
            </h1>
            <p className="text-gray-400 text-lg">
              Let our AI analyze your tax document and find savings opportunities
            </p>
          </div>

          {/* Tab Navigation */}
          <Tabs value={activeTab} onValueChange={(value: any) => setActiveTab(value)} className="mb-8">
            <TabsList className="grid w-full grid-cols-2 bg-slate-700/50">
              <TabsTrigger value="upload">Upload PDF</TabsTrigger>
              <TabsTrigger value="manual">Enter Manually</TabsTrigger>
            </TabsList>

            {/* Upload Tab */}
            <TabsContent value="upload">
              <Card className="bg-slate-800 border-slate-700 p-8">
                <FileUpload onUpload={handleFileUpload} disabled={uploadState.status === "uploading"} />
              </Card>
            </TabsContent>

            {/* Manual Entry Tab */}
            <TabsContent value="manual">
              <Card className="bg-slate-800 border-slate-700 p-8">
                <ManualInput onSubmit={handleManualSubmit} disabled={uploadState.status === "uploading"} />
              </Card>
            </TabsContent>
          </Tabs>

          {/* Status Messages */}
          {uploadState.status !== "idle" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex items-start gap-4 p-4 rounded-lg border ${
                uploadState.status === "uploading"
                  ? "bg-blue-500/10 border-blue-500/30"
                  : uploadState.status === "success"
                  ? "bg-green-500/10 border-green-500/30"
                  : "bg-red-500/10 border-red-500/30"
              }`}
            >
              {uploadState.status === "uploading" ? (
                <Loader className="w-5 h-5 text-blue-400 animate-spin mt-0.5 flex-shrink-0" />
              ) : uploadState.status === "success" ? (
                <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
              )}
              <div className="flex-1">
                <p
                  className={
                    uploadState.status === "uploading"
                      ? "text-blue-200"
                      : uploadState.status === "success"
                      ? "text-green-200"
                      : "text-red-200"
                  }
                >
                  {uploadState.message}
                </p>
              </div>
            </motion.div>
          )}

          {/* Info Box */}
          <div className="mt-12 bg-purple-500/10 border border-purple-500/20 rounded-lg p-6">
            <h3 className="font-semibold text-purple-200 mb-3">📋 What we need:</h3>
            <ul className="text-gray-400 space-y-2 text-sm">
              <li>✓ Your complete Form 16 (both pages recommended)</li>
              <li>✓ Clear PDF or scanned document</li>
              <li>✓ All salary components and deductions</li>
              <li>✓ TDS deducted amount</li>
            </ul>
          </div>

          {/* Security Info */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>🔒 Your Form 16 is encrypted and processed securely. We never store your documents.</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}