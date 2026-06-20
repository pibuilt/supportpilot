import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ArrowRight, Bot, FileStack, Gauge, MessageSquareText, Search, Ticket } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { documentsApi, exportsApi, healthApi, sessionsApi } from "@/lib/api";
import { formatDate, formatRelativeNumber } from "@/lib/utils";
import { useAuth } from "@/features/auth/auth-context";

export function DashboardPage() {
  const { user, hasApiKey } = useAuth();
  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    enabled: hasApiKey,
  });
  const sessionsQuery = useQuery({
    queryKey: ["sessions"],
    queryFn: sessionsApi.list,
    enabled: hasApiKey,
  });
  const analysesQuery = useQuery({
    queryKey: ["analyses-preview"],
    queryFn: () => exportsApi.preview<Array<Record<string, unknown>>>("analyses"),
    enabled: hasApiKey,
  });
  const healthQuery = useQuery({ queryKey: ["health"], queryFn: healthApi.status });

  const statCards = [
    {
      label: "Documents",
      value: documentsQuery.data ? formatRelativeNumber(documentsQuery.data.length) : "—",
      icon: FileStack,
    },
    {
      label: "Sessions",
      value: sessionsQuery.data ? formatRelativeNumber(sessionsQuery.data.length) : "—",
      icon: MessageSquareText,
    },
    {
      label: "Analyses",
      value: analysesQuery.data ? formatRelativeNumber(analysesQuery.data.length) : "—",
      icon: Search,
    },
  ];

  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <Card className="overflow-hidden bg-[linear-gradient(135deg,_rgba(19,32,41,0.98),_rgba(35,88,77,0.92))] text-white">
          <p className="text-xs uppercase tracking-[0.3em] text-white/50">Workspace overview</p>
          <h3 className="mt-3 max-w-xl text-3xl font-semibold">
            A single control plane for ingestion, contract review, semantic retrieval, and AI support.
          </h3>
          <p className="mt-3 max-w-2xl text-sm text-white/70">
            This dashboard is composed from the backend routes already present in the repository, including async job
            polling, export APIs, JWT auth, and API-key protected product workflows.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              className="inline-flex items-center rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-950"
              to="/documents"
            >
              Upload documents
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link
              className="inline-flex items-center rounded-full border border-white/20 px-4 py-2 text-sm font-semibold text-white"
              to="/assistant"
            >
              Open assistant
            </Link>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900">System status</p>
              <p className="mt-1 text-sm text-slate-500">Health is read from `/health`.</p>
            </div>
            <Gauge className="h-5 w-5 text-slate-400" />
          </div>
          <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            {healthQuery.isLoading ? (
              <Skeleton className="h-20" />
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <Badge tone={healthQuery.data?.status === "ok" ? "success" : "danger"}>
                    {healthQuery.data?.status ?? "Unknown"}
                  </Badge>
                  <span className="text-sm text-slate-500">{formatDate(new Date().toISOString())}</span>
                </div>
                <p className="mt-3 text-sm text-slate-600">
                  Signed in as <span className="font-semibold text-slate-900">{user?.full_name}</span> for tenant{" "}
                  <span className="font-semibold text-slate-900">{user?.tenant_id}</span>.
                </p>
              </>
            )}
          </div>
          <div className="mt-4 grid gap-3">
            <QuickAction to="/assistant?mode=search" label="Run semantic search" icon={Search} />
            <QuickAction to="/assistant?mode=analyze" label="Analyze a contract" icon={AlertCircle} />
            <QuickAction to="/tickets" label="Create support ticket" icon={Ticket} />
            <QuickAction to="/assistant" label="Ask the AI assistant" icon={Bot} />
          </div>
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {statCards.map((card) => (
          <Card key={card.label}>
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">{card.label}</p>
              <card.icon className="h-5 w-5 text-slate-400" />
            </div>
            <p className="mt-6 text-4xl font-semibold text-slate-950">
              {documentsQuery.isLoading || sessionsQuery.isLoading || analysesQuery.isLoading ? "..." : card.value}
            </p>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Recent sessions</h3>
              <p className="mt-1 text-sm text-slate-500">Latest orchestration conversations persisted by the backend.</p>
            </div>
          </div>
          <div className="mt-5 space-y-3">
            {!hasApiKey ? (
              <EmptyState
                title="Product API key required"
                description="Sign in succeeded, but product features stay paused until you store a valid API key again."
              />
            ) : sessionsQuery.isLoading ? (
              <>
                <Skeleton className="h-20" />
                <Skeleton className="h-20" />
              </>
            ) : sessionsQuery.data?.length ? (
              sessionsQuery.data.slice(0, 4).map((session) => (
                <div key={session.id} className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-slate-900">{session.title || `Session ${session.id.slice(0, 8)}`}</p>
                    <Badge tone="neutral">{session.message_count} messages</Badge>
                  </div>
                  <p className="mt-2 text-sm text-slate-500">Updated {formatDate(session.updated_at)}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">No sessions yet. Start a conversation from the assistant page.</p>
            )}
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-slate-950">Delivery notes</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-600">
            <p>The backend currently returns analysis data through direct analysis and export APIs, so this page composes those routes instead of relying on a dedicated analytics summary endpoint.</p>
            <p>Signed-in operators can use product routes immediately, while the API Keys page now handles issuing, rotating, and revoking integration credentials.</p>
            <p>Containerized deployments should set `VITE_API_BASE_URL=/api` and let Nginx reverse proxy requests to `api-gateway` inside Compose.</p>
          </div>
        </Card>
      </section>
    </div>
  );
}

function QuickAction({
  to,
  label,
  icon: Icon,
}: {
  to: string;
  label: string;
  icon: typeof Search;
}) {
  return (
    <Link className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3" to={to}>
      <div className="flex items-center gap-3">
        <div className="rounded-2xl bg-orange-50 p-2 text-orange-700">
          <Icon className="h-4 w-4" />
        </div>
        <span className="text-sm font-medium text-slate-900">{label}</span>
      </div>
      <ArrowRight className="h-4 w-4 text-slate-400" />
    </Link>
  );
}
