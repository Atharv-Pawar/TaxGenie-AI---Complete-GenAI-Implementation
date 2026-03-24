"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Zap, Shield, TrendingUp, Clock,
  ChevronRight, Star, IndianRupee,
} from "lucide-react";

const FEATURES = [
  {
    icon: <Zap className="w-5 h-5" />,
    title: "Smart PDF Parsing",
    desc: "Upload your Form 16 and our AI extracts every number in seconds.",
  },
  {
    icon: <IndianRupee className="w-5 h-5" />,
    title: "Find Missed Deductions",
    desc: "Average Indian misses ₹18,000+ in deductions. We find them all.",
  },
  {
    icon: <TrendingUp className="w-5 h-5" />,
    title: "Old vs New Regime",
    desc: "Exact rupee-for-rupee comparison with a clear recommendation.",
  },
  {
    icon: <Shield className="w-5 h-5" />,
    title: "Investment Plan",
    desc: "Personalised tax-saving investments matched to your risk profile.",
  },
];

const STATS = [
  { value: "₹18,500", label: "Avg deductions found" },
  { value: "90 sec", label: "Time to complete analysis" },
  { value: "₹3,500", label: "Avg CA fee saved" },
  { value: "99.98%", label: "Faster than a CA" },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-surface text-slate-100 overflow-x-hidden">

      {/* ── Navbar ── */}
      <nav className="fixed top-0 inset-x-0 z-50 border-b border-surface-border/50 backdrop-blur-md bg-surface/80">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="text-xl font-bold genie-text">🧞 TaxGenie AI</span>
          <div className="flex items-center gap-3">
            <Link href="/upload" className="text-sm text-slate-400 hover:text-white transition-colors">
              Analyze Taxes
            </Link>
            <Link
              href="/upload"
              className="px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="pt-32 pb-20 px-4 relative">
        {/* Background mesh */}
        <div className="absolute inset-0 bg-dark-mesh opacity-60 pointer-events-none" />

        <motion.div
          className="max-w-4xl mx-auto text-center relative z-10"
          variants={container}
          initial="hidden"
          animate="show"
        >
          <motion.div variants={item} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-medium mb-6">
            <Star className="w-3 h-3 fill-brand-400" />
            ET AI Hackathon 2026 — Problem Statement #9
          </motion.div>

          <motion.h1 variants={item} className="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Stop Overpaying{" "}
            <span className="genie-text">₹18,500</span>{" "}
            in Taxes Every Year
          </motion.h1>

          <motion.p variants={item} className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            Upload your Form 16. Our AI finds every missed deduction, compares
            Old vs New Regime with exact numbers, and builds your personalised
            investment plan — in under 90 seconds.
          </motion.p>

          <motion.div variants={item} className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/upload"
              className="group inline-flex items-center gap-2 px-8 py-4 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-lg transition-all duration-200 animate-pulse-glow"
            >
              Analyse My Taxes Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 px-8 py-4 bg-surface-card border border-surface-border hover:border-brand-500/50 text-white font-semibold rounded-xl text-lg transition-all duration-200"
            >
              Ask Tax Questions
              <ChevronRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Stats ── */}
      <section className="py-12 px-4 border-y border-surface-border">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {STATS.map((s) => (
            <motion.div
              key={s.label}
              className="text-center"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4 }}
            >
              <div className="text-3xl font-extrabold genie-text">{s.value}</div>
              <div className="text-sm text-slate-500 mt-1">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Priya Story ── */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.div
            className="bg-surface-card border border-surface-border rounded-2xl p-8"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-brand-500/20 flex items-center justify-center text-brand-400 font-bold">P</div>
              <div>
                <div className="font-semibold">Meet Priya</div>
                <div className="text-sm text-slate-500">28-year-old software developer, ₹12 LPA</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                <div className="text-red-400 font-semibold mb-2">❌ Before TaxGenie</div>
                <p className="text-sm text-slate-400">
                  Pays ₹1,20,000 in taxes. Picked New Regime randomly without calculating.
                  Missed HRA, 80C gap, and NPS benefits.
                </p>
              </div>
              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                <div className="text-green-400 font-semibold mb-2">✅ After TaxGenie</div>
                <p className="text-sm text-slate-400">
                  Saves <strong className="text-green-400">₹23,000</strong> by switching regime + claiming HRA
                  + investing ₹46,800 in ELSS. Done in <strong className="text-green-400">47 seconds</strong>.
                </p>
              </div>
            </div>

            <div className="mt-4 text-center text-sm text-slate-500">
              A CA would charge ₹3,000 and take 3 days. TaxGenie: free, 47 seconds.
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-20 px-4 bg-surface-card/30">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Everything your CA does — in 90 seconds</h2>
          <p className="text-center text-slate-400 mb-12">Powered by GPT-4o + Claude 3.5 Sonnet + LangGraph</p>

          <div className="grid md:grid-cols-2 gap-6">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                className="flex gap-4 p-6 bg-surface-card border border-surface-border rounded-2xl card-glow"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="w-10 h-10 rounded-lg bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 flex-shrink-0">
                  {f.icon}
                </div>
                <div>
                  <div className="font-semibold mb-1">{f.title}</div>
                  <div className="text-sm text-slate-400">{f.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 px-4">
        <motion.div
          className="max-w-2xl mx-auto text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <div className="text-5xl mb-4">🧞</div>
          <h2 className="text-4xl font-extrabold mb-4">
            Your wish is a <span className="genie-text">₹18,500 tax saving</span>
          </h2>
          <p className="text-slate-400 mb-8">
            Upload your Form 16 and let TaxGenie find every rupee you're leaving on the table.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-10 py-5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xl transition-all duration-200"
          >
            Analyse My Taxes Now <ArrowRight className="w-6 h-6" />
          </Link>
          <p className="mt-4 text-sm text-slate-600">Free • No sign-up required • 90 seconds</p>
        </motion.div>
      </section>

      {/* ── Footer ── */}
      <footer className="py-8 px-4 border-t border-surface-border text-center text-sm text-slate-600">
        Built with ❤️ for ET AI Hackathon 2026 · Powered by Anthropic Claude + OpenAI GPT-4o
      </footer>
    </main>
  );
}
