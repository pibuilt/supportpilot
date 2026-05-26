import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        mist: "#f4f4f0",
        sand: "#e7e2d9",
        ember: "#b8542f",
        pine: "#23584d",
        slate: "#475569",
      },
      fontFamily: {
        sans: ["Aptos", "Segoe UI", "Helvetica Neue", "sans-serif"],
        mono: ["IBM Plex Mono", "Consolas", "monospace"],
      },
      boxShadow: {
        panel: "0 20px 50px rgba(17, 24, 39, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
