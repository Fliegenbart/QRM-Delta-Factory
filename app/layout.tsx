import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pharma QRM Delta Engine",
  description: "AI-assisted draft Quality Risk Management delta engine MVP"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
