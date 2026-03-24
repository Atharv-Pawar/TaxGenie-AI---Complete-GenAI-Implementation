"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-lg border-b border-slate-700/50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <span className="text-3xl">🧞‍♂️</span>
          <span className="font-bold text-white hidden sm:inline">
            Tax<span className="text-purple-400">Genie</span>
          </span>
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-8">
          <Link href="/" className="text-gray-300 hover:text-white transition">
            Home
          </Link>
          <Link href="/upload" className="text-gray-300 hover:text-white transition">
            Upload
          </Link>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Link href="/upload">Get Started</Link>
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-gray-300"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden bg-slate-800 border-t border-slate-700 py-4"
        >
          <div className="container mx-auto px-4 flex flex-col gap-4">
            <Link href="/" className="text-gray-300 hover:text-white">
              Home
            </Link>
            <Link href="/upload" className="text-gray-300 hover:text-white">
              Upload
            </Link>
            <Button className="w-full bg-purple-600 hover:bg-purple-700">
              <Link href="/upload">Get Started</Link>
            </Button>
          </div>
        </motion.div>
      )}
    </nav>
  );
}