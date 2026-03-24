"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTaxStore } from "@/store/taxStore";
import { cn } from "@/lib/utils";
import { MessageCircle, LayoutDashboard, Upload, Home } from "lucide-react";

const NAV_LINKS = [
  { href: "/",          label: "Home",      icon: <Home className="w-4 h-4" /> },
  { href: "/upload",    label: "Analyse",   icon: <Upload className="w-4 h-4" /> },
  { href: "/dashboard", label: "Dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
  { href: "/chat",      label: "Chat",      icon: <MessageCircle className="w-4 h-4" /> },
];

export default function Navbar() {
  const pathname = usePathname();
  const sessionId = useTaxStore((s) => s.sessionId);

  return (
    <nav className="fixed top-0 inset-x-0 z-50 border-b border-surface-border/50 backdrop-blur-md bg-surface/80">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-lg font-bold genie-text">
          🧞 TaxGenie AI
        </Link>

        <div className="flex items-center gap-1">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                pathname === link.href
                  ? "bg-brand-500/10 text-brand-400"
                  : "text-slate-400 hover:text-white hover:bg-surface-card"
              )}
            >
              {link.icon}
              <span className="hidden sm:block">{link.label}</span>
            </Link>
          ))}

          {sessionId && (
            <div className="ml-2 px-2 py-1 rounded bg-green-500/10 border border-green-500/20 text-green-400 text-xs">
              Session Active
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
