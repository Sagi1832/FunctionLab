import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Optional dev proxy to avoid CORS. If you enable it, also set baseURL to "/api" in src/api/client.js later.
    // proxy: {
    //   "/api": {
    //     target: process.env.VITE_API_BASE_URL || "http://localhost:8000",
    //     changeOrigin: true,
    //     rewrite: (p) => p.replace(/^\/api/, ""),
    //   },
    // },
  },
});
