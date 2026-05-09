import type { Metadata } from "next";
import { Providers } from "@/src/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pharma QRM Delta Engine",
  description: "AI-assisted draft Quality Risk Management delta engine MVP"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="de" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#ffffff" />
        {/* Prevent flash of wrong theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('pharma-qrm-theme');
                  var isDark = theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches);
                  if (isDark) {
                    document.documentElement.classList.add('dark');
                    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', '#0f172a');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body>
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
