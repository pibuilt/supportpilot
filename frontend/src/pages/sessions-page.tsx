import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/features/auth/auth-context";
import { sessionsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export function SessionsPage() {
  const { hasApiKey } = useAuth();
  const sessionsQuery = useQuery({
    queryKey: ["sessions"],
    queryFn: sessionsApi.list,
    enabled: hasApiKey,
  });
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const detailQuery = useQuery({
    queryKey: ["session", activeSessionId],
    queryFn: () => sessionsApi.get(activeSessionId!),
    enabled: hasApiKey && Boolean(activeSessionId),
  });

  return (
    <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
      <Card>
        <h3 className="text-lg font-semibold text-slate-950">All sessions</h3>
        <div className="mt-5 space-y-3">
          {!hasApiKey ? (
            <EmptyState
              title="Product API key required"
              description="Session history is available after you add a valid product API key."
            />
          ) : sessionsQuery.isLoading ? (
            <>
              <Skeleton className="h-20" />
              <Skeleton className="h-20" />
            </>
          ) : sessionsQuery.data?.length ? (
            sessionsQuery.data.map((session) => (
              <button
                key={session.id}
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left"
                onClick={() => setActiveSessionId(session.id)}
                type="button"
              >
                <p className="font-medium text-slate-900">{session.title || `Session ${session.id.slice(0, 8)}`}</p>
                <p className="mt-1 text-sm text-slate-500">
                  {session.message_count} messages • {formatDate(session.updated_at)}
                </p>
              </button>
            ))
          ) : (
            <EmptyState title="No sessions found" description="Assistant conversations will appear here after orchestration jobs complete." />
          )}
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-slate-950">Conversation history</h3>
        <div className="mt-5 space-y-4">
          {detailQuery.isLoading ? (
            <Skeleton className="h-80" />
          ) : detailQuery.data ? (
            detailQuery.data.messages.map((message) => (
              <div
                key={message.id}
                className={`max-w-[85%] rounded-3xl px-4 py-3 ${
                  message.role === "assistant"
                    ? "bg-slate-100 text-slate-900"
                    : "ml-auto bg-slate-900 text-white"
                }`}
              >
                <p className="text-xs uppercase tracking-[0.2em] opacity-60">{message.role}</p>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{message.content}</p>
              </div>
            ))
          ) : (
            <EmptyState title="Select a session" description="Pick a conversation from the list to inspect its message history." />
          )}
        </div>
      </Card>
    </div>
  );
}
