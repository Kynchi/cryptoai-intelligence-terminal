import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#080B12",
          panel: "#0F1520",
          panel2: "#141C2E",
          panel3: "#1A2338",
          accent: "#63B3ED",
          text: "#E8EDF5",
          muted: "#8B98AE",
          success: "#48BB78",
          danger: "#FC8181",
          warning: "#F6C90E"
        }
      },
      fontFamily: {
        outfit: ["Outfit", "sans-serif"],
        inter: ["Inter", "sans-serif"],
        mono: ["DM Mono", "monospace"]
      },
      boxShadow: {
        glow: "0 0 36px rgba(99, 179, 237, 0.16)"
      }
    }
  },
  plugins: []
};

export default config;
