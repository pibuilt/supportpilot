export const TOKEN_KEY = "token";
export const API_KEY = "api_key";
export const AUTH_EVENT = "supportpilot:logout";
export const ASSISTANT_ACTIVE_JOB_KEY = "assistant_active_job_id";
export const ASSISTANT_ACTIVE_SESSION_KEY = "assistant_active_session_id";
export const ASSISTANT_PENDING_PROMPT_KEY = "assistant_pending_prompt";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getApiKey() {
  return localStorage.getItem(API_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function setApiKey(apiKey: string) {
  localStorage.setItem(API_KEY, apiKey);
}

export function clearSessionStorage() {
  localStorage.removeItem(TOKEN_KEY);
}

export function clearApiKeyStorage() {
  localStorage.removeItem(API_KEY);
}

export function clearAuthStorage() {
  clearSessionStorage();
  clearApiKeyStorage();
}

export function triggerLogoutEvent() {
  window.dispatchEvent(new CustomEvent(AUTH_EVENT));
}

export function getSessionValue(key: string) {
  return window.sessionStorage.getItem(key);
}

export function setSessionValue(key: string, value: string) {
  window.sessionStorage.setItem(key, value);
}

export function clearSessionValue(key: string) {
  window.sessionStorage.removeItem(key);
}
