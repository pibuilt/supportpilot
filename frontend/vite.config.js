import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
export default defineConfig(function (_a) {
    var _b;
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd(), "");
    var apiBaseUrl = (_b = env.VITE_API_BASE_URL) !== null && _b !== void 0 ? _b : "/api";
    return {
        plugins: [react()],
        resolve: {
            alias: {
                "@": path.resolve(__dirname, "./src"),
            },
        },
        server: {
            host: "0.0.0.0",
            port: 5173,
            proxy: apiBaseUrl === "/api"
                ? {
                    "/api": {
                        target: "http://localhost:8000",
                        changeOrigin: true,
                        rewrite: function (requestPath) {
                            return requestPath.replace(/^\/api/, "");
                        },
                    },
                }
                : undefined,
        },
    };
});
