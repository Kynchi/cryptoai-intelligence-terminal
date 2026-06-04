import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  },
  server: {
    proxy: {
      "/terminal": "http://localhost:8000",
      "/predict": "http://localhost:8000",
      "/backtest": "http://localhost:8000",
      "/realtime": "http://localhost:8000",
      "/leaderboard": "http://localhost:8000",
      "/health": "http://localhost:8000"
    }
  },
  build: {
    target: "es2022",
    cssCodeSplit: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          charts: ["echarts", "echarts-for-react", "recharts"],
          motion: ["framer-motion"]
        }
      }
    }
  }
});
