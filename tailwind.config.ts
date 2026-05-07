import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172026",
        mist: "#f5f7f8",
        line: "#d9e1e5",
        teal: "#137c78",
        amber: "#b7791f",
        danger: "#b42318"
      }
    }
  },
  plugins: []
};

export default config;
