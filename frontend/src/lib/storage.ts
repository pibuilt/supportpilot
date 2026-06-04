export const TOKEN_KEY = "token";
export const API_KEY = "api_key";
export const AUTH_EVENT = "supportpilot:logout";
export const ASSISTANT_ACTIVE_JOB_KEY = "assistant_active_job_id";
export const ASSISTANT_ACTIVE_SESSION_KEY = "assistant_active_session_id";
export const ASSISTANT_PENDING_PROMPT_KEY = "assistant_pending_prompt";
export const ASSISTANT_ACTIVE_UPLOAD_JOB_KEY = "assistant_active_upload_job_id";
export const ASSISTANT_ACTIVE_UPLOAD_DOCUMENT_KEY = "assistant_active_upload_document_id";
export const DOCUMENTS_ACTIVE_JOB_KEY = "documents_active_job_id";
export const DOCUMENTS_ACTIVE_JOB_DOCUMENT_KEY = "documents_active_job_document_id";

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
  clearSessionValue(ASSISTANT_ACTIVE_JOB_KEY);
  clearSessionValue(ASSISTANT_ACTIVE_SESSION_KEY);
  clearSessionValue(ASSISTANT_PENDING_PROMPT_KEY);
  clearSessionValue(ASSISTANT_ACTIVE_UPLOAD_JOB_KEY);
  clearSessionValue(ASSISTANT_ACTIVE_UPLOAD_DOCUMENT_KEY);
  clearSessionValue(DOCUMENTS_ACTIVE_JOB_KEY);
  clearSessionValue(DOCUMENTS_ACTIVE_JOB_DOCUMENT_KEY);
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
