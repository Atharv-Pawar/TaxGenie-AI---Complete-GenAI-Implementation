"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mail, Lock, Eye, EyeOff, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);

    // Simulate auth — replace with real auth logic (NextAuth / Supabase / etc.)
    await new Promise((r) => setTimeout(r, 1200));

    // For hackathon: skip auth and go directly to upload
    // In production: verify credentials then redirect
    setLoading(false);
    router.push("/upload");
  };

  const handleGuestAccess = () => {
    // Allow users to skip login and use TaxGenie directly
    router.push("/upload");
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      {/* Background mesh */}
      <div className="absolute inset-0 bg-dark-mesh opacity-50 pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🧞</div>
          <h1 className="text-2xl font-extrabold genie-text">TaxGenie AI</h1>
          <p className="text-slate-400 text-sm mt-1">
            Your Personal Tax Wizard
          </p>
        </div>

        {/* Card */}
        <div className="bg-surface-card border border-surface-border rounded-2xl p-8">
          <h2 className="text-xl font-bold mb-1">Welcome back</h2>
          <p className="text-slate-400 text-sm mb-6">
            Sign in to access your tax analysis
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="priya@example.com"
                  autoComplete="email"
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-surface border border-surface-border text-slate-200 placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 transition-colors"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-medium text-slate-300">
                  Password
                </label>
                <Link
                  href="#"
                  className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  className="w-full pl-10 pr-10 py-3 rounded-xl bg-surface border border-surface-border text-slate-200 placeholder-slate-600 text-sm focus:outline-none focus:border-brand-500/60 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword
                    ? <EyeOff className="w-4 h-4" />
                    : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Error message */}
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
              >
                ⚠️ {error}
              </motion.p>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm flex items-center justify-center gap-2 transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-surface-border" />
            <span className="text-xs text-slate-600">or</span>
            <div className="flex-1 h-px bg-surface-border" />
          </div>

          {/* Guest access */}
          <button
            onClick={handleGuestAccess}
            className="w-full py-3 rounded-xl bg-surface border border-surface-border hover:border-brand-500/40 text-slate-300 hover:text-white font-medium text-sm transition-all"
          >
            Continue without signing in (Guest)
          </button>

          {/* Sign up link */}
          <p className="text-center text-sm text-slate-500 mt-5">
            Don&apos;t have an account?{" "}
            <Link
              href="#"
              className="text-brand-400 hover:text-brand-300 font-medium transition-colors"
            >
              Create one free
            </Link>
          </p>
        </div>

        {/* Footer note */}
        <p className="text-center text-xs text-slate-600 mt-4">
          Your data is never stored permanently · Secured with encryption
        </p>
      </motion.div>
    </div>
  );
}
