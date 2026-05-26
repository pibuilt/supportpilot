import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { AxiosError } from "axios";
import {
  Download,
  FileSearch,
  Files,
  LoaderCircle,
  MessageSquareText,
  Paperclip,
  ScanSearch,
  Send,
  Upload,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input, Textarea } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useAuth } from "@/features/auth/auth-context";
import { useJobPolling } from "@/hooks/use-job-polling";
import { analysisApi, documentsApi, exportsApi, orchestrationApi, searchApi, sessionsApi } from "@/lib/api";
import {
  ASSISTANT_ACTIVE_JOB_KEY,
  ASSISTANT_ACTIVE_SESSION_KEY,
  ASSISTANT_PENDING_PROMPT_KEY,
  clearSessionValue,
  getSessionValue,
  setSessionValue,
} from "@/lib/storage";
import { useToast } from "@/lib/toast";
import { downloadBlob, formatDate, truncate } from "@/lib/utils";
import type { AnalysisPayload, OrchestrationPayload, SearchResult, SessionSummary } from "@/types/api";

type AssistantMode = "chat" | "search" | "analyze";

interface LocalMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  mode: AssistantMode;
  searchResults?: SearchResult[];
  analysis?: AnalysisPayload;
}

const modeOptions: Array<{
  id: AssistantMode;
  label: string;
  icon: typeof MessageSquareText;
}> = [
  { id: "chat", label: "Chat", icon: MessageSquareText },
  { id: "search", label: "Search", icon: FileSearch },
  { id: "analyze", label: "Analyze", icon: ScanSearch },
];

export function AssistantPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(() =>
    getSessionValue(ASSISTANT_ACTIVE_SESSION_KEY),
  );
  const [activeJobId, setActiveJobId] = useState<string | null>(() =>
    getSessionValue(ASSISTANT_ACTIVE_JOB_KEY),
  );
  const [pendingPrompt, setPendingPrompt] = useState(() => getSessionValue(ASSISTANT_PENDING_PROMPT_KEY) ?? "");
  const [localMessages, setLocalMessages] = useState<LocalMessage[]>([]);
  const [message, setMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [showUploadPanel, setShowUploadPanel] = useState(false);
  const [uploadDocumentId, setUploadDocumentId] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [activeUploadJobId, setActiveUploadJobId] = useState<string | null>(null);

  const mode = normalizeMode(searchParams.get("mode"));
  const activeChatJobQuery = useJobPolling<OrchestrationPayload>(activeJobId);
  const activeUploadJobQuery = useJobPolling(activeUploadJobId);

  const sessionsQuery = useQuery({
    queryKey: ["sessions"],
    queryFn: sessionsApi.list,
    enabled: hasApiKey,
  });

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    enabled: hasApiKey,
  });

  const activeSessionQuery = useQuery({
    queryKey: ["session", selectedSessionId],
    queryFn: () => sessionsApi.get(selectedSessionId!),
    enabled: hasApiKey && Boolean(selectedSessionId),
  });

  const uploadMutation = useMutation({
    mutationFn: documentsApi.uploadFile,
    onSuccess: (data) => {
      setActiveUploadJobId(data.job_id);
      appendLocalMessage({
        role: "system",
        mode: "chat",
        content: `Document "${uploadDocumentId}" is being ingested and will be available for Search and Analyze shortly.`,
      });
      setShowUploadPanel(false);
      push({ tone: "info", title: "Document queued", description: `${uploadDocumentId} is being ingested.` });
    },
    onError: (error) => {
      const messageText = error instanceof AxiosError ? error.response?.data?.detail : "Upload failed";
      push({ tone: "error", title: "Upload failed", description: String(messageText) });
    },
  });

  const chatMutation = useMutation({
    mutationFn: orchestrationApi.create,
    onSuccess: (data) => {
      setActiveJobId(data.job_id);
      setPendingPrompt(message.trim());
      setMessage("");
    },
    onError: (error) => {
      const messageText = error instanceof AxiosError ? error.response?.data?.detail : "Chat request failed";
      push({ tone: "error", title: "Assistant request failed", description: String(messageText) });
    },
  });

  const searchMutation = useMutation({
    mutationFn: searchApi.run,
    onSuccess: (data, variables) => {
      appendLocalMessage({
        role: "user",
        mode: "search",
        content: `Search request: ${variables.query}${variables.document_id ? ` in ${variables.document_id}` : ""}`,
      });
      appendLocalMessage({
        role: "assistant",
        mode: "search",
        content:
          data.results.length > 0
            ? `Found ${data.summary.matches_found} matching result${data.summary.matches_found === 1 ? "" : "s"}.`
            : "No matches found for that search.",
        searchResults: data.results,
      });
      setSearchQuery("");
    },
    onError: (error) => {
      const messageText = error instanceof AxiosError ? error.response?.data?.detail : "Search failed";
      push({ tone: "error", title: "Search failed", description: String(messageText) });
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: analysisApi.run,
    onSuccess: (data, currentDocumentId) => {
      appendLocalMessage({
        role: "user",
        mode: "analyze",
        content: `Analyze document: ${currentDocumentId}`,
      });
      appendLocalMessage({
        role: "assistant",
        mode: "analyze",
        content: `Analysis complete for ${currentDocumentId}. Found ${data.summary.total_clauses} clauses with an overall ${data.executive_summary?.overall_risk ?? "unknown"} risk profile.`,
        analysis: data,
      });
    },
    onError: (error) => {
      const messageText = error instanceof AxiosError ? error.response?.data?.detail : "Analysis failed";
      push({ tone: "error", title: "Analysis failed", description: String(messageText) });
    },
  });

  useEffect(() => {
    if (selectedSessionId) {
      setSessionValue(ASSISTANT_ACTIVE_SESSION_KEY, selectedSessionId);
      return;
    }
    clearSessionValue(ASSISTANT_ACTIVE_SESSION_KEY);
  }, [selectedSessionId]);

  useEffect(() => {
    if (activeJobId) {
      setSessionValue(ASSISTANT_ACTIVE_JOB_KEY, activeJobId);
      return;
    }
    clearSessionValue(ASSISTANT_ACTIVE_JOB_KEY);
  }, [activeJobId]);

  useEffect(() => {
    if (pendingPrompt) {
      setSessionValue(ASSISTANT_PENDING_PROMPT_KEY, pendingPrompt);
      return;
    }
    clearSessionValue(ASSISTANT_PENDING_PROMPT_KEY);
  }, [pendingPrompt]);

  useEffect(() => {
    if (!selectedSessionId && sessionsQuery.data?.length) {
      setSelectedSessionId(sessionsQuery.data[0].id);
    }
  }, [selectedSessionId, sessionsQuery.data]);

  useEffect(() => {
    if (activeChatJobQuery.data?.status === "COMPLETED" && activeChatJobQuery.data.result?.session_id) {
      setSelectedSessionId(activeChatJobQuery.data.result.session_id);
      setActiveJobId(null);
      setPendingPrompt("");
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["session", activeChatJobQuery.data.result.session_id] });
      push({ tone: "success", title: "Assistant response ready" });
    }

    if (activeChatJobQuery.data?.status === "FAILED" || activeChatJobQuery.data?.status === "DEAD_LETTER") {
      setActiveJobId(null);
      push({ tone: "error", title: "Assistant request failed" });
    }
  }, [activeChatJobQuery.data, push, queryClient]);

  useEffect(() => {
    if (activeUploadJobQuery.data?.status === "COMPLETED") {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setActiveUploadJobId(null);
      setUploadProgress(0);
      setSelectedFile(null);
      if (uploadDocumentId) {
        setDocumentId(uploadDocumentId);
        appendLocalMessage({
          role: "system",
          mode: "chat",
          content: `Document "${uploadDocumentId}" is ready. Use Search or Analyze mode to work with it.`,
        });
      }
      setUploadDocumentId("");
      push({ tone: "success", title: "Document ready", description: "You can use it from Search or Analyze mode now." });
    }

    if (activeUploadJobQuery.data?.status === "FAILED" || activeUploadJobQuery.data?.status === "DEAD_LETTER") {
      setActiveUploadJobId(null);
      push({ tone: "error", title: "Document ingestion failed" });
    }
  }, [activeUploadJobQuery.data?.status, push, queryClient, uploadDocumentId]);

  function appendLocalMessage(messageItem: Omit<LocalMessage, "id">) {
    setLocalMessages((current) => [...current, { ...messageItem, id: crypto.randomUUID() }]);
  }

  async function handleChatSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before chatting" });
      return;
    }

    if (!message.trim()) {
      return;
    }

    await chatMutation.mutateAsync({
      query: message.trim(),
      document_id: documentId || undefined,
      session_id: selectedSessionId || undefined,
      context_limit: 5,
    });
  }

  async function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before searching" });
      return;
    }

    if (!searchQuery.trim()) {
      push({ tone: "error", title: "Enter a search query first" });
      return;
    }

    await searchMutation.mutateAsync({
      query: searchQuery.trim(),
      document_id: documentId || undefined,
      top_k: 5,
    });
  }

  async function handleAnalyzeSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before analyzing" });
      return;
    }

    if (!documentId) {
      push({ tone: "error", title: "Select a document to analyze" });
      return;
    }

    await analyzeMutation.mutateAsync(documentId);
  }

  async function handleUploadSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before uploading" });
      return;
    }

    if (!selectedFile || !uploadDocumentId) {
      push({ tone: "error", title: "Choose a file and document ID first" });
      return;
    }

    await uploadMutation.mutateAsync({
      documentId: uploadDocumentId,
      file: selectedFile,
      onUploadProgress: setUploadProgress,
    });
  }

  function switchMode(nextMode: AssistantMode) {
    setSearchParams(nextMode === "chat" ? {} : { mode: nextMode });
  }

  async function exportSessions(format: "json" | "csv") {
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before exporting chats" });
      return;
    }

    const payload = await exportsApi.download("sessions", format);
    downloadBlob(payload.blob, payload.filename);
  }

  async function exportAnalyses(format: "json" | "csv") {
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before exporting analyses" });
      return;
    }

    const payload = await exportsApi.download("analyses", format);
    downloadBlob(payload.blob, payload.filename);
  }

  const sessions = sessionsQuery.data ?? [];
  const combinedMessages = useMemo(() => {
    const persisted =
      activeSessionQuery.data?.messages.map((entry) => ({
        id: entry.id,
        role: entry.role as "user" | "assistant",
        content: entry.content,
        mode: "chat" as AssistantMode,
      })) ?? [];

    const workingMessages = [...persisted];

    if (pendingPrompt) {
      workingMessages.push({
        id: "pending-user",
        role: "user",
        content: pendingPrompt,
        mode: "chat",
      });
    }

    if (activeChatJobQuery.data?.status === "PENDING" || activeChatJobQuery.data?.status === "PROCESSING" || chatMutation.isPending) {
      workingMessages.push({
        id: "pending-assistant",
        role: "assistant",
        content: "Thinking through your request...",
        mode: "chat",
      });
    }

    return [...workingMessages, ...localMessages];
  }, [activeChatJobQuery.data?.status, activeSessionQuery.data?.messages, chatMutation.isPending, localMessages, pendingPrompt]);

  return (
    <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
      <Card className="flex h-[calc(100vh-11rem)] flex-col overflow-hidden p-0">
        <div className="border-b border-slate-200 px-5 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Chats</h3>
              <p className="mt-1 text-sm text-slate-500">Gateway-backed assistant session history</p>
            </div>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setSelectedSessionId(null);
                setLocalMessages([]);
                setPendingPrompt("");
                setMessage("");
                setSearchQuery("");
              }}
            >
              <Files className="mr-2 h-4 w-4" />
              New
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto px-4 py-4">
          {!hasApiKey ? (
            <EmptyState
              title="Product API key required"
              description="Restore a valid product API key to open the assistant workspace."
            />
          ) : sessions.length ? (
            <div className="space-y-2">
              {sessions.map((session: SessionSummary) => (
                <button
                  key={session.id}
                  className={`w-full rounded-2xl px-4 py-3 text-left transition ${
                    selectedSessionId === session.id
                      ? "bg-slate-900 text-white"
                      : "bg-white text-slate-900 hover:bg-slate-50"
                  }`}
                  onClick={() => {
                    setSelectedSessionId(session.id);
                    setLocalMessages([]);
                    setPendingPrompt("");
                  }}
                  type="button"
                >
                  <p className="truncate text-sm font-semibold">{session.title || `Session ${session.id.slice(0, 8)}`}</p>
                  <p className={`mt-1 text-xs ${selectedSessionId === session.id ? "text-white/70" : "text-slate-500"}`}>
                    {session.message_count} messages • {formatDate(session.updated_at)}
                  </p>
                </button>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No chats yet"
              description="Start with Chat, Search, or Analyze. Search and Analyze results will appear in this workspace too."
            />
          )}
        </div>
      </Card>

      <Card className="flex h-[calc(100vh-11rem)] flex-col overflow-hidden p-0">
        <div className="border-b border-slate-200 px-6 py-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h3 className="text-xl font-semibold text-slate-950">SupportPilot Assistant</h3>
              <p className="mt-1 text-sm text-slate-500">
                One workspace for conversational help, document search, and contract analysis.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button type="button" variant="secondary" onClick={() => exportSessions("json")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                Export chats JSON
              </Button>
              <Button type="button" variant="secondary" onClick={() => exportSessions("csv")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                Export chats CSV
              </Button>
              <Button type="button" variant="secondary" onClick={() => exportAnalyses("json")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                Export analyses
              </Button>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-2">
            {modeOptions.map((option) => (
              <button
                key={option.id}
                className={`inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold transition ${
                  mode === option.id
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
                onClick={() => switchMode(option.id)}
                type="button"
              >
                <option.icon className="mr-2 h-4 w-4" />
                {option.label}
              </button>
            ))}

            <Button type="button" variant="secondary" onClick={() => setShowUploadPanel((current) => !current)}>
              <Paperclip className="mr-2 h-4 w-4" />
              Ingest document
            </Button>
          </div>

          {showUploadPanel ? (
            <form className="mt-4 rounded-3xl border border-slate-200 bg-slate-50 p-4" onSubmit={handleUploadSubmit}>
              <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
                <Input
                  value={uploadDocumentId}
                  onChange={(event) => setUploadDocumentId(event.target.value)}
                  placeholder="Document ID"
                />
                <Button type="button" variant="secondary" onClick={() => fileInputRef.current?.click()}>
                  <Upload className="mr-2 h-4 w-4" />
                  {selectedFile ? selectedFile.name : "Choose file"}
                </Button>
                <Button type="submit" disabled={uploadMutation.isPending || !selectedFile || !uploadDocumentId}>
                  Upload
                </Button>
              </div>
              <input
                ref={fileInputRef}
                className="hidden"
                type="file"
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null;
                  setSelectedFile(file);
                  if (file && !uploadDocumentId) {
                    setUploadDocumentId(file.name.replace(/\.[^/.]+$/, "").replace(/\s+/g, "-").toLowerCase());
                  }
                }}
              />
              {(uploadMutation.isPending || activeUploadJobId) && (
                <div className="mt-3 rounded-2xl bg-white px-3 py-3 text-sm text-slate-600">
                  <div className="flex items-center justify-between">
                    <span>
                      {uploadMutation.isPending
                        ? "Uploading document..."
                        : `Ingestion ${activeUploadJobQuery.data?.status?.toLowerCase() ?? "queued"}...`}
                    </span>
                    <span>{uploadMutation.isPending ? `${uploadProgress}%` : activeUploadJobQuery.data?.status ?? "QUEUED"}</span>
                  </div>
                </div>
              )}
            </form>
          ) : null}
        </div>

        <div className="flex-1 overflow-auto bg-[#fbfaf7] px-6 py-6">
          <div className="mx-auto flex max-w-4xl flex-col gap-5">
            {combinedMessages.length ? (
              combinedMessages.map((messageItem) => (
                <AssistantMessageCard key={messageItem.id} message={messageItem} />
              ))
            ) : (
              <div className="py-16 text-center">
                <p className="text-sm uppercase tracking-[0.28em] text-slate-400">Customer-first workflow</p>
                <h4 className="mt-3 text-3xl font-semibold text-slate-950">Chat when you need help, switch modes when you need precision</h4>
                <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-slate-500">
                  Chat mode uses your existing orchestration backend. Search mode finds matching document chunks. Analyze mode runs contract analysis on a selected document.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-slate-200 bg-white px-6 py-5">
          {!hasApiKey ? (
            <EmptyState
              title="Product API key required"
              description="Restore a valid product API key to use the assistant."
            />
          ) : (
            <div className="mx-auto max-w-4xl">
              {mode === "chat" ? (
                <form onSubmit={handleChatSubmit}>
                  <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-3">
                    <Textarea
                      rows={3}
                      value={message}
                      onChange={(event) => setMessage(event.target.value)}
                      placeholder="Ask SupportPilot for help with a customer issue, workflow, or general question..."
                      className="border-0 bg-transparent px-2 py-2 text-sm shadow-none focus:border-0"
                    />
                    <div className="mt-3 flex items-center justify-between gap-3">
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        <Badge tone="neutral">{documentId ? `Scoped to ${documentId}` : "Using all knowledge"}</Badge>
                        {activeJobId ? <Badge tone="warning">{activeChatJobQuery.data?.status ?? "Processing"}</Badge> : null}
                      </div>
                      <Button type="submit" disabled={chatMutation.isPending || !message.trim()}>
                        <Send className="mr-2 h-4 w-4" />
                        Send
                      </Button>
                    </div>
                  </div>
                </form>
              ) : mode === "search" ? (
                <form onSubmit={handleSearchSubmit}>
                  <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-4">
                    <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
                      <Input
                        value={searchQuery}
                        onChange={(event) => setSearchQuery(event.target.value)}
                        placeholder="Search uploaded documents for specific terms, clauses, or passages..."
                      />
                      <Select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
                        <option value="">All ingested knowledge</option>
                        {documentsQuery.data?.map((document) => (
                          <option key={document.document_id} value={document.document_id}>
                            {document.document_id}
                          </option>
                        ))}
                      </Select>
                      <Button type="submit" disabled={searchMutation.isPending || !searchQuery.trim()}>
                        <FileSearch className="mr-2 h-4 w-4" />
                        Search
                      </Button>
                    </div>
                  </div>
                </form>
              ) : (
                <form onSubmit={handleAnalyzeSubmit}>
                  <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-4">
                    <div className="grid gap-3 md:grid-cols-[1fr_auto]">
                      <Select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
                        <option value="">Select a document to analyze</option>
                        {documentsQuery.data?.map((document) => (
                          <option key={document.document_id} value={document.document_id}>
                            {document.document_id}
                          </option>
                        ))}
                      </Select>
                      <Button type="submit" disabled={analyzeMutation.isPending || !documentId}>
                        <ScanSearch className="mr-2 h-4 w-4" />
                        Analyze
                      </Button>
                    </div>
                    <p className="mt-3 text-xs text-slate-500">
                      Analyze mode intentionally removes the free-text prompt and keeps the action focused on a selected document.
                    </p>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

function normalizeMode(value: string | null): AssistantMode {
  if (value === "search" || value === "analyze") {
    return value;
  }

  return "chat";
}

function AssistantMessageCard({ message }: { message: LocalMessage }) {
  if (message.role === "system") {
    return (
      <div className="rounded-[24px] border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-600">
        {message.content}
      </div>
    );
  }

  if (message.role === "user") {
    return (
      <div className="ml-auto max-w-[85%] rounded-[28px] bg-slate-900 px-5 py-4 text-white">
        <p className="text-[11px] uppercase tracking-[0.22em] opacity-55">
          {message.mode === "search" ? "search request" : message.mode === "analyze" ? "analysis request" : "user"}
        </p>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-7">{message.content}</p>
      </div>
    );
  }

  const isPending = message.id === "pending-assistant";

  return (
    <div className="max-w-[85%] rounded-[28px] bg-white px-5 py-4 text-slate-800 shadow-sm">
      <p className="text-[11px] uppercase tracking-[0.22em] opacity-55">
        {message.mode === "search" ? "search result" : message.mode === "analyze" ? "analysis result" : "assistant"}
      </p>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-7">{message.content}</p>

      {message.searchResults?.length ? (
        <div className="mt-4 space-y-3">
          {message.searchResults.map((result) => (
            <div key={`${result.document_id}-${result.chunk_id}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="neutral">{result.document_id}</Badge>
                <Badge tone="accent">Chunk {result.chunk_id.slice(0, 8)}</Badge>
                <Badge tone="success">Score {result.score.toFixed(3)}</Badge>
              </div>
              <p className="mt-3 text-sm text-slate-700">{result.chunk_text || result.preview}</p>
            </div>
          ))}
        </div>
      ) : null}

      {message.analysis ? (
        <div className="mt-4 space-y-3">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-900">{message.analysis.document_id}</p>
            <p className="mt-2 text-sm text-slate-600">
              {message.analysis.summary.total_clauses} clauses • overall risk {message.analysis.executive_summary?.overall_risk ?? "unknown"}
            </p>
          </div>
          {message.analysis.clauses.slice(0, 5).map((clause, index) => (
            <div key={`${clause.clause_type}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="neutral">{clause.clause_type}</Badge>
                <Badge
                  tone={
                    clause.metadata.risk_level === "high"
                      ? "danger"
                      : clause.metadata.risk_level === "medium"
                        ? "warning"
                        : "success"
                  }
                >
                  {String(clause.metadata.risk_level ?? "low")} risk
                </Badge>
              </div>
              <p className="mt-3 text-sm text-slate-700">{truncate(clause.matched_text, 220)}</p>
            </div>
          ))}
        </div>
      ) : null}

      {isPending ? (
        <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
          <LoaderCircle className="h-4 w-4 animate-spin" />
          Generating...
        </div>
      ) : null}
    </div>
  );
}
