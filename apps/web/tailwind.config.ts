import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        slate: "#374151",
        mist: "#eef2f7",
        brand: "#0f766e",
        accent: "#f59e0b",
        danger: "#dc2626"
      },
      boxShadow: {
        panel: "0 18px 50px rgba(15, 23, 42, 0.12)"
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Iowan Old Style", "Palatino Linotype", "serif"]
      }
    }
  },
  plugins: []
};

export default config;

