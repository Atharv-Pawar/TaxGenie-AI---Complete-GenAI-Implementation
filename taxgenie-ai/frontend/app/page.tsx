"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Shield, Zap, TrendingUp, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 },
  };

  const staggerContainer = {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <>
      {/* Hero Section */}
      <section className="relative min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600/20 rounded-full blur-3xl animate-pulse delay-75"></div>
        </div>

        <div className="relative container mx-auto px-4 py-20">
          <motion.div
            className="text-center max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Logo */}
            <motion.div
              className="text-7xl md:text-8xl mb-8 drop-shadow-lg"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              🧞‍♂️
            </motion.div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Tax<span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                Genie
              </span>{" "}
              AI
            </h1>

            {/* Subheadline */}
            <p className="text-2xl md:text-3xl text-gray-300 mb-4 font-light">
              Upload your Form 16. Save thousands in taxes.{" "}
              <span className="font-semibold text-purple-400">In 30 seconds.</span>
            </p>

            {/* Description */}
            <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              AI-powered tax optimization that identifies missed deductions, compares tax
              regimes, and creates your personalized savings plan.
            </p>

            {/* CTA Button */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link href="/upload">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 
                           text-white font-semibold py-6 px-10 text-lg rounded-full
                           shadow-lg shadow-purple-500/50 hover:shadow-purple-500/75 transition-all"
                >
                  <span className="mr-2">📄</span>
                  Upload Form 16
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
            </motion.div>

            <p className="text-gray-500 text-sm mt-6">
              🔒 Your data stays private. All processing happens securely.
            </p>
          </motion.div>

          {/* Trust Indicators */}
          <motion.div
            className="flex flex-wrap justify-center gap-8 mt-20"
            variants={staggerContainer}
            initial="initial"
            animate="animate"
          >
            {[
              { icon: "🛡️", text: "GDPR Compliant" },
              { icon: "🔐", text: "Bank-grade Security" },
              { icon: "⚡", text: "Instant Results" },
              { icon: "🇮🇳", text: "India Tax Laws 2024-25" },
            ].map((badge, idx) => (
              <motion.div
                key={idx}
                className="flex items-center gap-2 text-gray-400"
                variants={fadeInUp}
              >
                <span className="text-xl">{badge.icon}</span>
                <span>{badge.text}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <motion.h2
            className="text-4xl font-bold text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            Why Choose TaxGenie?
          </motion.h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                icon: <Shield className="w-12 h-12" />,
                title: "Find Missed Deductions",
                description:
                  "AI scans your Form 16 and identifies every tax-saving opportunity you're missing",
              },
              {
                icon: <TrendingUp className="w-12 h-12" />,
                title: "Old vs New Regime",
                description:
                  "Get exact calculations for both regimes with your specific numbers",
              },
              {
                icon: <Zap className="w-12 h-12" />,
                title: "Investment Recommendations",
                description:
                  "Personalized suggestions ranked by your risk profile and liquidity needs",
              },
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                className="bg-slate-700/50 backdrop-blur border border-slate-600 rounded-2xl p-8
                           hover:border-purple-500/50 transition-all duration-300"
                whileHover={{ translateY: -5 }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="text-purple-400 mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gradient-to-b from-slate-900 to-slate-800/50">
        <div className="container mx-auto px-4">
          <motion.h2
            className="text-4xl font-bold text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            How It Works
          </motion.h2>

          <div className="grid md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {[
              { step: 1, icon: "📤", title: "Upload Form 16", desc: "Drag & drop your PDF or enter details" },
              { step: 2, icon: "🤖", title: "AI Analyzes", desc: "Our AI runs comprehensive analysis" },
              { step: 3, icon: "📊", title: "See Savings", desc: "View all tax-saving opportunities" },
              { step: 4, icon: "💬", title: "Get Guidance", desc: "Chat with Tax AI for clarifications" },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                className="text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center 
                              text-white font-bold mx-auto mb-4 text-xl">
                  {item.step}
                </div>
                <div className="text-4xl mb-2">{item.icon}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {[
              { value: "₹45,000", label: "Avg. Tax Saved" },
              { value: "95%", label: "Indians Without Plan" },
              { value: "30 sec", label: "Analysis Time" },
              { value: "100%", label: "Free to Use" },
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                className="text-center"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl font-bold text-purple-400 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <motion.h2
            className="text-4xl font-bold mb-4"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Ready to Save on Taxes?
          </motion.h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Join thousands of Indians who optimized their taxes with TaxGenie AI
          </p>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link href="/upload">
              <Button
                size="lg"
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700
                         text-white font-semibold py-6 px-12 text-lg rounded-full
                         shadow-lg shadow-purple-500/50"
              >
                Get Started Free <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
    </>
  );
}