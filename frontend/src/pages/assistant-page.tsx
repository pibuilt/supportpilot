import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Send, Sparkles } from "lucide-react";
import { AxiosError } from "axios";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useAuth } from "@/features/auth/auth-context";
import { documentsApi, orchestrationApi, sessionsApi } from "@/lib/api";
import {
  ASSISTANT_ACTIVE_JOB_KEY,
  ASSISTANT_ACTIVE_SESSION_KEY,
  clearSessionValue,
  getSessionValue,
  setSessionValue,
} from "@/lib/storage";
import { useJobPolling } from "@/hooks/use-job-polling";
import { formatDate } from "@/lib/utils";
import { useToast } from "@/lib/toast";
import type { OrchestrationPayload } from "@/types/api";

export function AssistantPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const queryClient = useQueryClient();
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
  const [activeSessionId, setActiveSessionId] = useState<string | null>(() => getSessionValue(ASSISTANT_ACTIVE_SESSION_KEY));
  const [documentId, setDocumentId] = useState("");
  const [contextLimit, setContextLimit] = useState(5);
  const [message, setMessage] = useState("");
  const [activeJobId, setActiveJobId] = useState<string | null>(() => getSessionValue(ASSISTANT_ACTIVE_JOB_KEY));

  const activeSessionQuery = useQuery({
    queryKey: ["session", activeSessionId],
    queryFn: () => sessionsApi.get(activeSessionId!),
    enabled: hasApiKey && Boolean(activeSessionId),
  });

  const activeJobQuery = useJobPolling<OrchestrationPayload>(activeJobId);

  const orchestrateMutation = useMutation({
    mutationFn: orchestrationApi.create,
    onSuccess: (data) => {
      setActiveJobId(data.job_id);
      setMessage("");
    },
    onError: (error) => {
      const messageText = error instanceof AxiosError ? error.response?.data?.detail : "Request failed";
      push({ tone: "error", title: "Assistant request failed", description: String(messageText) });
    },
  });

  useEffect(() => {
    if (activeJobQuery.data?.status === "COMPLETED" && activeJobQuery.data.result?.session_id) {
      setActiveSessionId(activeJobQuery.data.result.session_id);
      clearSessionValue(ASSISTANT_ACTIVE_JOB_KEY);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["session", activeJobQuery.data.result.session_id] });
      push({ tone: "success", title: "Assistant response ready" });
    }
  }, [activeJobQuery.data, push, queryClient]);

  useEffect(() => {
    if (activeJobId) {
      setSessionValue(ASSISTANT_ACTIVE_JOB_KEY, activeJobId);
      return;
    }

    clearSessionValue(ASSISTANT_ACTIVE_JOB_KEY);
  }, [activeJobId]);

  useEffect(() => {
    if (activeSessionId) {
      setSessionValue(ASSISTANT_ACTIVE_SESSION_KEY, activeSessionId);
      return;
    }

    clearSessionValue(ASSISTANT_ACTIVE_SESSION_KEY);
  }, [activeSessionId]);

  useEffect(() => {
    const status = activeJobQuery.data?.status;
    if (status === "COMPLETED" || status === "FAILED" || status === "DEAD_LETTER") {
      setActiveJobId(null);
    }
  }, [activeJobQuery.data?.status]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before using the assistant" });
      return;
    }
    await orchestrateMutation.mutateAsync({
      query: message,
      document_id: documentId || undefined,
      session_id: activeSessionId || undefined,
      context_limit: contextLimit,
    });
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.82fr_1.18fr]">
      <Card className="xl:max-h-[calc(100vh-12rem)] xl:overflow-auto">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Session history</h3>
            <p className="mt-1 text-sm text-slate-500">Persisted chat sessions from `/v1/sessions`.</p>
          </div>
          <Button
            type="button"
            variant="secondary"
            onClick={() => {
              setActiveSessionId(null);
              setActiveJobId(null);
            }}
          >
            New chat
          </Button>
        </div>
        <div className="mt-5 space-y-3">
          {!hasApiKey ? (
            <EmptyState
              title="Product API key required"
              description="Assistant sessions and orchestration are disabled until a valid product API key is stored."
            />
          ) : sessionsQuery.data?.length ? (
            sessionsQuery.data.map((session) => (
              <button
                key={session.id}
                className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                  activeSessionId === session.id
                    ? "border-slate-900 bg-slate-900 text-white"
                    : "border-slate-200 bg-white text-slate-900"
                }`}
                onClick={() => setActiveSessionId(session.id)}
                type="button"
              >
                <p className="font-medium">{session.title || `Session ${session.id.slice(0, 8)}`}</p>
                <p className={`mt-1 text-sm ${activeSessionId === session.id ? "text-white/70" : "text-slate-500"}`}>
                  {session.message_count} messages • {formatDate(session.updated_at)}
                </p>
              </button>
            ))
          ) : (
            <EmptyState title="No assistant sessions" description="Send your first orchestration request to start a chat history." />
          )}
        </div>
      </Card>

      <div className="space-y-6">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">AI assistant</h3>
              <p className="mt-1 text-sm text-slate-500">This posts to `/v1/orchestrate` and polls the async job result.</p>
            </div>
            <Badge tone="accent">Async orchestration</Badge>
          </div>
          <form className="mt-5 grid gap-4 md:grid-cols-[0.9fr_0.35fr_1fr_auto]" onSubmit={handleSubmit}>
            <Select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
              <option value="">All documents</option>
              {documentsQuery.data?.map((document) => (
                <option key={document.document_id} value={document.document_id}>
                  {document.document_id}
                </option>
              ))}
            </Select>
            <Input min={1} max={20} type="number" value={contextLimit} onChange={(event) => setContextLimit(Number(event.target.value))} />
            <Input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask for a summary, retrieval, or contract interpretation..." required />
            <Button type="submit" disabled={orchestrateMutation.isPending || !hasApiKey}>
              <Send className="mr-2 h-4 w-4" />
              Send
            </Button>
          </form>
          {activeJobQuery.data ? (
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-3">
                <Sparkles className="h-4 w-4 text-slate-400" />
                <Badge tone={activeJobQuery.data.status === "COMPLETED" ? "success" : "warning"}>
                  {activeJobQuery.data.status}
                </Badge>
              </div>
              <p className="mt-2 text-sm text-slate-500">Job ID: {activeJobQuery.data.job_id}</p>
              {activeJobQuery.data.error_message ? (
                <p className="mt-2 text-sm text-rose-700">{activeJobQuery.data.error_message}</p>
              ) : null}
            </div>
          ) : null}
        </Card>

        <Card className="min-h-[28rem]">
          <h3 className="text-lg font-semibold text-slate-950">Conversation</h3>
          <div className="mt-5 space-y-4">
            {activeSessionQuery.data?.messages.length ? (
              activeSessionQuery.data.messages.map((entry) => (
                <div
                  key={entry.id}
                  className={`max-w-[85%] rounded-3xl px-4 py-3 ${
                    entry.role === "assistant"
                      ? "bg-white text-slate-800 shadow-sm"
                      : "ml-auto bg-slate-900 text-white"
                  }`}
                >
                  <p className="text-xs uppercase tracking-[0.2em] opacity-60">{entry.role}</p>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{entry.content}</p>
                </div>
              ))
            ) : activeJobQuery.data?.result?.tone?.final_response ? (
              <div className="max-w-[85%] rounded-3xl bg-white px-4 py-3 text-slate-800 shadow-sm">
                <p className="text-xs uppercase tracking-[0.2em] opacity-60">assistant</p>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-6">
                  {String(activeJobQuery.data.result.tone.final_response)}
                </p>
              </div>
            ) : (
              <EmptyState title="No conversation selected" description="Choose a session from the left or send a new message." />
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
