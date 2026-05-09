import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Primary colors with improved contrast ratios (WCAG AA compliant)
        ink: "#172026",
        mist: "#f5f7f8",
        line: "#c8d1d6", // Darker for better contrast (was #d9e1e5)

        // Teal scale for brand and interactive elements
        teal: {
          DEFAULT: "#009b8d",
          50: "#f0fdf9",
          100: "#ccfbf1",
          200: "#99f6e4",
          300: "#5eead4",
          400: "#2dd4bf",
          500: "#009b8d", // Brand color
          600: "#008577", // Text on white (4.5:1 contrast)
          700: "#006b5f", // Text on light gray (7:1 contrast)
          800: "#005249",
          900: "#003d33",
        },

        // Amber scale for warnings
        amber: {
          DEFAULT: "#b7791f",
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#b7791f", // Warning color (WCAG AA on white)
          600: "#92610a", // Darker for better contrast
          700: "#78500f",
          800: "#5c3d10",
          900: "#422c0d",
        },

        // Danger scale for errors and critical items
        danger: {
          DEFAULT: "#b42318",
          50: "#fef2f2",
          100: "#fee2e2",
          200: "#fecaca",
          300: "#fca5a5",
          400: "#f87171",
          500: "#b42318", // Error color (WCAG AA on white)
          600: "#991b1b",
          700: "#7f1d1d",
          800: "#601410",
          900: "#450a0a",
        },

        // Success color
        success: {
          DEFAULT: "#047857",
          500: "#047857",
          600: "#065f46",
        },
      },

      // Improved text colors for better readability
      textColor: {
        primary: "#172026",
        secondary: "#475569", // Improved from slate-500 for WCAG AA
        tertiary: "#64748b",
        muted: "#94a3b8",
      },

      // Animation for loading states
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 2s linear infinite",
      },
    }
  },
  plugins: []
};

export default config;
