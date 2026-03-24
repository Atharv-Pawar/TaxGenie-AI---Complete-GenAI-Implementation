import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/shared/Providers";

export const metadata: Metadata = {
  title: "TaxGenie AI — Your Personal Tax Wizard 🧞",
  description:
    "AI-native tax planning for every Indian. Upload Form 16, find deductions, compare regimes, and get a personalised investment plan in under 60 seconds.",
  keywords: ["tax planning", "Form 16", "income tax", "India", "AI", "deductions"],
  openGraph: {
    title: "TaxGenie AI",
    description: "Turning India's tax complexity into a 90-second conversation",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-surface font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
