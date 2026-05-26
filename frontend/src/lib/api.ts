import axios from "axios";
import { appConfig } from "@/lib/config";
import {
  clearSessionStorage,
  getApiKey,
  getToken,
  triggerLogoutEvent,
} from "@/lib/storage";
import type {
  AdminUser,
  AnalysisPayload,
  AsyncJob,
  AuthResponse,
  CurrentUser,
  DocumentDetail,
  DocumentSummary,
  HealthPayload,
  OrchestrationPayload,
  SearchPayload,
  SessionDetail,
  SessionSummary,
  TicketCreateResponse,
  TicketDetail,
  TicketListResponse,
  TicketSearchResponse,
  ValidationPayload,
} from "@/types/api";

const baseURL = appConfig.apiBaseUrl;

const bearerClient = axios.create({
  baseURL,
});

const productClient = axios.create({
  baseURL,
});

function handleUnauthorized() {
  clearSessionStorage();
  triggerLogoutEvent();
}

function getErrorDetail(error: unknown) {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof error.response === "object" &&
    error.response !== null &&
    "data" in error.response
  ) {
    const data = error.response.data;
    if (typeof data === "object" && data !== null && "detail" in data) {
      return String(data.detail);
    }
  }

  return "";
}

bearerClient.interceptors.request.use((config) => {
  const token = getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

productClient.interceptors.request.use((config) => {
  const apiKey = getApiKey();

  if (apiKey) {
    config.headers["x-api-key"] = apiKey;
  }

  return config;
});

bearerClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      handleUnauthorized();
    }

    return Promise.reject(error);
  },
);

productClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  },
);

type SuccessEnvelope<T> = {
  data: T;
  request_id: string;
};

export const authApi = {
  async login(payload: { email: string; password: string }) {
    const { data } = await bearerClient.post<AuthResponse>("/v1/auth/login", payload);
    return data;
  },
  async signup(payload: {
    email: string;
    password: string;
    full_name: string;
    tenant_id: string;
  }) {
    const { data } = await bearerClient.post<AuthResponse>("/v1/auth/signup", payload);
    return data;
  },
  async me() {
    const { data } = await bearerClient.get<CurrentUser>("/v1/auth/me");
    return data;
  },
};

export const healthApi = {
  async status() {
    const { data } = await bearerClient.get<SuccessEnvelope<HealthPayload>>("/health");
    return data.data;
  },
};

export const documentsApi = {
  async list() {
    const { data } = await productClient.get<{ items: DocumentSummary[] }>("/v1/documents");
    return data.items;
  },
  async get(documentId: string) {
    const { data } = await productClient.get<DocumentDetail>(`/v1/documents/${documentId}`);
    return data;
  },
  async remove(documentId: string) {
    const { data } = await productClient.delete(`/v1/documents/${documentId}`);
    return data;
  },
  async uploadFile(payload: {
    documentId: string;
    file: File;
    onUploadProgress?: (progress: number) => void;
  }) {
    const formData = new FormData();
    formData.append("document_id", payload.documentId);
    formData.append("file", payload.file);

    const { data } = await productClient.post<SuccessEnvelope<{ job_id: string; status: string }>>(
      "/v1/ingest/file",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (event) => {
          if (event.total && payload.onUploadProgress) {
            payload.onUploadProgress(Math.round((event.loaded / event.total) * 100));
          }
        },
      },
    );

    return data.data;
  },
};

export const jobsApi = {
  async get<T>(jobId: string) {
    const { data } = await productClient.get<AsyncJob<T>>(`/v1/jobs/${jobId}`);
    return data;
  },
};

export const searchApi = {
  async run(payload: { query: string; document_id?: string; top_k?: number }) {
    const { data } = await productClient.post<SuccessEnvelope<SearchPayload>>("/v1/search", payload);
    return data.data;
  },
};

export const analysisApi = {
  async run(documentId: string) {
    const { data } = await productClient.post<SuccessEnvelope<AnalysisPayload>>("/v1/analyze", {
      document_id: documentId,
    });
    return data.data;
  },
};

export const orchestrationApi = {
  async create(payload: {
    query: string;
    document_id?: string;
    session_id?: string;
    context_limit?: number;
  }) {
    const { data } = await productClient.post<{ job_id: string; status: string }>(
      "/v1/orchestrate",
      payload,
    );
    return data;
  },
};

export const sessionsApi = {
  async list() {
    const { data } = await productClient.get<{ items: SessionSummary[] }>("/v1/sessions");
    return data.items;
  },
  async get(sessionId: string) {
    const { data } = await productClient.get<SessionDetail>(`/v1/sessions/${sessionId}`);
    return data;
  },
};

export const exportsApi = {
  async download(kind: "documents" | "sessions" | "analyses", format: "json" | "csv") {
    const response = await productClient.get(`/v1/export/${kind}`, {
      params: { format },
      responseType: "blob",
    });

    return {
      blob: response.data as Blob,
      filename: `${kind}.${format}`,
    };
  },
  async preview<T>(kind: "documents" | "sessions" | "analyses") {
    const { data } = await productClient.get<T>(`/v1/export/${kind}`, {
      params: { format: "json" },
    });

    return data;
  },
};

export const apiKeysApi = {
  async validate() {
    const apiKey = getApiKey();
    const { data } = await bearerClient.get<ValidationPayload>("/v1/api-keys/validate", {
      headers: {
        "x-api-key": apiKey ?? "",
      },
    });
    return data;
  },
};

export const adminApi = {
  async listUsers() {
    const { data } = await bearerClient.get<AdminUser[]>("/v1/admin/users");
    return data;
  },
  async suspendUser(userId: string) {
    const { data } = await bearerClient.patch<{ message: string }>(`/v1/admin/users/${userId}/suspend`);
    return data;
  },
  async activateUser(userId: string) {
    const { data } = await bearerClient.patch<{ message: string }>(`/v1/admin/users/${userId}/activate`);
    return data;
  },
  async promoteUser(userId: string) {
    const { data } = await bearerClient.patch<{ message: string }>(`/v1/admin/users/${userId}/promote`);
    return data;
  },
  async demoteUser(userId: string) {
    const { data } = await bearerClient.patch<{ message: string }>(`/v1/admin/users/${userId}/demote`);
    return data;
  },
  async revokeApiKey(apiKeyId: string) {
    const { data } = await bearerClient.patch<{ message: string }>(
      `/v1/admin/api-keys/${apiKeyId}/revoke`,
    );
    return data;
  },
  async regenerateApiKey(apiKeyId: string) {
    const { data } = await bearerClient.patch<{ message: string; new_api_key: string }>(
      `/v1/admin/api-keys/${apiKeyId}/regenerate`,
    );
    return data;
  },
};

export const ticketsApi = {
  async create(payload: { ticket_text: string }) {
    const { data } = await productClient.post<TicketCreateResponse>("/v1/tickets", payload);
    return data;
  },
  async list(params?: { status?: string; limit?: number; offset?: number }) {
    const { data } = await productClient.get<TicketListResponse>("/v1/tickets", {
      params,
    });
    return data;
  },
  async get(ticketId: string) {
    const { data } = await productClient.get<TicketDetail>(`/v1/tickets/${ticketId}`);
    return data;
  },
  async search(query: string, limit = 5) {
    const { data } = await productClient.get<TicketSearchResponse>("/v1/tickets/search/query", {
      params: { q: query, limit },
    });
    return data;
  },
};
