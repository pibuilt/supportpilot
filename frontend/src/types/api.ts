export type UserRole = "user" | "admin" | "root_admin";

export interface AuthResponse {
  access_token: string;
  token_type: string;
  api_key: string;
  key_prefix: string;
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  tenant_id: string;
}

export interface CurrentUser {
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  tenant_id: string;
  is_active: boolean;
}

export interface DocumentSummary {
  document_id: string;
  chunk_count: number;
  embedding_model: string;
  embedding_version: string;
}

export interface DocumentDetail extends DocumentSummary {
  chunks: Array<{
    chunk_id: string;
    chunk_text: string;
  }>;
}

export interface AsyncJob<T = unknown> {
  job_id: string;
  job_type: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED" | "DEAD_LETTER";
  retry_count: number;
  error_message: string | null;
  result: T | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface SearchResult {
  document_id: string;
  chunk_id: string;
  chunk_text?: string;
  preview?: string;
  score: number;
  semantic_score?: number;
  keyword_score?: number;
  rerank_score?: number;
}

export interface SearchPayload {
  owner_id: string;
  tenant_id: string;
  query: string;
  summary: {
    matches_found: number;
  };
  results: SearchResult[];
}

export interface ClauseFinding {
  clause_type: string;
  matched_text: string;
  confidence_score: number;
  metadata: Record<string, unknown>;
  risk_level?: string;
}

export interface AnalysisPayload {
  owner_id: string;
  tenant_id: string;
  document_id: string;
  clauses: ClauseFinding[];
  summary: {
    total_clauses: number;
    by_type: Record<string, number>;
  };
  executive_summary?: {
    overall_risk: string;
    high_risk_count: number;
    medium_risk_count: number;
    low_risk_count: number;
    critical_clauses: string[];
  };
}

export interface SessionSummary {
  id: string;
  title: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail extends SessionSummary {
  messages: Array<{
    id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
  }>;
}

export interface OrchestrationPayload {
  request_id: string;
  session_id: string;
  triage: Record<string, unknown>;
  tool_decision?: Record<string, unknown> | null;
  tool_output?: Record<string, unknown> | null;
  specialist: Record<string, unknown>;
  tone: {
    final_response?: string;
    [key: string]: unknown;
  };
}

export interface HealthPayload {
  status: string;
  timestamp: number;
}

export interface ValidationPayload {
  valid: boolean;
  owner?: string;
  role?: string;
  tenant_id?: string;
}

export interface AdminUser {
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  tenant_id: string;
  is_active: boolean;
}

export interface TicketCreateResponse {
  ticket_id: string;
  status: string;
  category: string;
  priority: string;
  message: string;
}

export interface TicketListItem {
  ticket_id: string;
  ticket_text: string;
  status: string;
  category: string;
  priority: string;
  created_at?: string;
}

export interface TicketListResponse {
  total: number;
  count: number;
  tickets: TicketListItem[];
}

export interface TicketDetail extends TicketListItem {
  updated_at?: string;
}

export interface TicketSearchResponse {
  query: string;
  count: number;
  tickets: TicketListItem[];
}
