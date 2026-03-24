import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TaxGenie AI - Smart Tax Optimization",
  description:
    "AI-powered tax planning for Indian taxpayers. Upload your Form 16 and save thousands in taxes.",
  keywords:
    "tax, India, Form 16, tax saving, AI, TaxGenie, deductions, investment",
  authors: [{ name: "TaxGenie Team" }],
  creator: "TaxGenie AI",
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: "https://taxgenie.ai",
    title: "TaxGenie AI - Smart Tax Optimization",
    description: "Upload Form 16. Save thousands in taxes. In 30 seconds.",
    siteName: "TaxGenie AI",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="theme-color" content="#7c3aed" />
      </head>
      <body className={`${inter.className} bg-slate-900 text-white`}>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}