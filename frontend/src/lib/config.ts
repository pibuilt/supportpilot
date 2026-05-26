export const appConfig = {
  apiBaseUrl:
    window.__APP_CONFIG__?.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    "/api",
};
