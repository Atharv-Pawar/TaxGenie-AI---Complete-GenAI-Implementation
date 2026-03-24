import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
          300: "#fdba74",
          400: "#fb923c",
          500: "#f97316",
          600: "#ea580c",
          700: "#c2410c",
          800: "#9a3412",
          900: "#7c2d12",
        },
        surface: {
          DEFAULT: "#0f172a",
          card:    "#1e293b",
          elevated:"#293548",
          border:  "#334155",
        },
      },
      fontFamily: {
        sans: ["var(--font-plus-jakarta)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      backgroundImage: {
        "genie-gradient": "linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%)",
        "dark-mesh":
          "radial-gradient(at 20% 20%, hsla(215,91%,15%,1) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(25,95%,20%,1) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(220,70%,10%,1) 0px, transparent 50%)",
      },
      animation: {
        "fade-up":   "fadeUp 0.5s ease forwards",
        "pulse-glow":"pulseGlow 2s ease-in-out infinite",
        "spin-slow": "spin 3s linear infinite",
        "shimmer":   "shimmer 1.5s infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 0px rgba(249,115,22,0)" },
          "50%":       { boxShadow: "0 0 24px rgba(249,115,22,0.4)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
