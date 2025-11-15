import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const ensureApiBaseUrl = (mode) => {
  const apiBaseUrl = process.env.VITE_API_BASE_URL?.trim();

  if (!apiBaseUrl) {
    if (mode === "development") {
      console.warn("[Vite] VITE_API_BASE_URL not set - falling back to runtime inference.");
      return;
    }
    throw new Error("VITE_API_BASE_URL is required for the admin portal build");
  }

  if (mode === "production" && !apiBaseUrl.startsWith("https://")) {
    throw new Error("VITE_API_BASE_URL must use HTTPS when building for production");
  }
};

export default defineConfig(({ mode }) => {
  ensureApiBaseUrl(mode);

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: 5173,
      allowedHosts: ["host.docker.internal"]
    },
    preview: {
      host: "0.0.0.0",
      port: 4173
    }
  };
});
