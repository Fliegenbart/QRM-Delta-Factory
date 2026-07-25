import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/src/components/providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Pharma QRM Delta Engine",
  description: "AI-assisted draft Quality Risk Management delta engine MVP"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="de" className={inter.variable}>
      <head>
        <meta name="theme-color" content="#ffffff" />
      </head>
      <body>
        <a href="#main-content" className="skip-link">
          Zum Inhalt springen
        </a>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
