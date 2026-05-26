import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { Search as SearchIcon, Ticket, PlusCircle } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/features/auth/auth-context";
import { ticketsApi } from "@/lib/api";
import { useToast } from "@/lib/toast";
import { formatDate, truncate } from "@/lib/utils";

export function TicketsPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [ticketText, setTicketText] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);

  const ticketsQuery = useQuery({
    queryKey: ["tickets", status],
    queryFn: () => ticketsApi.list({ status: status || undefined }),
    enabled: hasApiKey,
  });

  const ticketDetailQuery = useQuery({
    queryKey: ["ticket", selectedTicketId],
    queryFn: () => ticketsApi.get(selectedTicketId!),
    enabled: hasApiKey && Boolean(selectedTicketId),
  });

  const searchMutation = useMutation({
    mutationFn: (query: string) => ticketsApi.search(query),
    onError: (error) => {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Search failed";
      push({ tone: "error", title: "Unable to search tickets", description: String(message) });
    },
  });

  const createMutation = useMutation({
    mutationFn: ticketsApi.create,
    onSuccess: (data) => {
      push({
        tone: "success",
        title: "Ticket created",
        description: `${data.category} • ${data.priority} priority`,
      });
      setTicketText("");
      setSelectedTicketId(data.ticket_id);
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
    },
    onError: (error) => {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Ticket creation failed";
      push({ tone: "error", title: "Unable to create ticket", description: String(message) });
    },
  });

  async function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before creating tickets" });
      return;
    }

    await createMutation.mutateAsync({ ticket_text: ticketText });
  }

  async function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before searching tickets" });
      return;
    }

    if (!searchQuery.trim()) {
      push({ tone: "error", title: "Enter a search term first" });
      return;
    }

    await searchMutation.mutateAsync(searchQuery.trim());
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <div className="space-y-6">
        {!hasApiKey ? (
          <EmptyState
            title="Product API key required"
            description="Ticket creation and listing are protected by `x-api-key`. Restore a valid product key to use this area."
          />
        ) : null}

        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Create support ticket</h3>
              <p className="mt-1 text-sm text-slate-500">
                Submit raw ticket text and let the backend classify category and priority automatically.
              </p>
            </div>
            <Badge tone="accent">Auto-triage</Badge>
          </div>
          <form className="mt-5 space-y-4" onSubmit={handleCreate}>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Ticket text</label>
              <Textarea
                rows={7}
                value={ticketText}
                onChange={(event) => setTicketText(event.target.value)}
                placeholder="Describe the support issue, symptoms, urgency, and any customer impact..."
              />
            </div>
            <Button type="submit" disabled={createMutation.isPending || !hasApiKey || !ticketText.trim()}>
              <PlusCircle className="mr-2 h-4 w-4" />
              {createMutation.isPending ? "Creating..." : "Create ticket"}
            </Button>
          </form>
        </Card>

        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Search tickets</h3>
              <p className="mt-1 text-sm text-slate-500">Search ticket text using the backend query route.</p>
            </div>
            <Badge tone="neutral">`/v1/tickets/search/query`</Badge>
          </div>
          <form className="mt-5 flex flex-col gap-3 md:flex-row" onSubmit={handleSearch}>
            <Input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search by issue description or keyword"
            />
            <Button type="submit" variant="secondary" disabled={searchMutation.isPending || !hasApiKey}>
              <SearchIcon className="mr-2 h-4 w-4" />
              Search
            </Button>
          </form>
          <div className="mt-4 space-y-3">
            {searchMutation.data?.tickets.length ? (
              searchMutation.data.tickets.map((ticket) => (
                <button
                  key={ticket.ticket_id}
                  className="w-full rounded-2xl border border-slate-200 bg-white p-4 text-left"
                  onClick={() => setSelectedTicketId(ticket.ticket_id)}
                  type="button"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone="neutral">{ticket.category}</Badge>
                    <Badge tone={priorityTone(ticket.priority)}>{ticket.priority}</Badge>
                    <Badge tone="accent">{ticket.status}</Badge>
                  </div>
                  <p className="mt-3 text-sm text-slate-700">{ticket.ticket_text}</p>
                </button>
              ))
            ) : searchMutation.isPending ? (
              <p className="text-sm text-slate-500">Searching tickets...</p>
            ) : null}
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Ticket queue</h3>
              <p className="mt-1 text-sm text-slate-500">Browse your support tickets with status filtering.</p>
            </div>
            <div className="w-full md:w-52">
              <Select value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value="">All statuses</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="pending">Pending</option>
              </Select>
            </div>
          </div>
          <div className="mt-5 space-y-3">
            {!hasApiKey ? (
              <EmptyState
                title="No API key available"
                description="Store a valid product API key to load ticket data."
              />
            ) : ticketsQuery.isLoading ? (
              <>
                <Skeleton className="h-20" />
                <Skeleton className="h-20" />
              </>
            ) : ticketsQuery.data?.tickets.length ? (
              ticketsQuery.data.tickets.map((ticket) => (
                <button
                  key={ticket.ticket_id}
                  className="w-full rounded-2xl border border-slate-200 bg-white p-4 text-left"
                  onClick={() => setSelectedTicketId(ticket.ticket_id)}
                  type="button"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone="neutral">{ticket.category}</Badge>
                    <Badge tone={priorityTone(ticket.priority)}>{ticket.priority}</Badge>
                    <Badge tone="accent">{ticket.status}</Badge>
                  </div>
                  <p className="mt-3 font-medium text-slate-900">{truncate(ticket.ticket_text, 110)}</p>
                  <p className="mt-2 text-sm text-slate-500">{formatDate(ticket.created_at)}</p>
                </button>
              ))
            ) : (
              <EmptyState
                title="No tickets yet"
                description="Create your first support ticket to start triage and queue management."
              />
            )}
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <Ticket className="h-5 w-5 text-slate-400" />
            <h3 className="text-lg font-semibold text-slate-950">Ticket details</h3>
          </div>
          <div className="mt-5">
            {ticketDetailQuery.isLoading ? (
              <Skeleton className="h-72" />
            ) : ticketDetailQuery.data ? (
              <div className="space-y-4">
                <div className="rounded-3xl bg-slate-50 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone="neutral">{ticketDetailQuery.data.category}</Badge>
                    <Badge tone={priorityTone(ticketDetailQuery.data.priority)}>{ticketDetailQuery.data.priority}</Badge>
                    <Badge tone="accent">{ticketDetailQuery.data.status}</Badge>
                  </div>
                  <p className="mt-3 text-sm font-medium text-slate-900">{ticketDetailQuery.data.ticket_id}</p>
                  <p className="mt-2 text-sm text-slate-500">
                    Created {formatDate(ticketDetailQuery.data.created_at)} • Updated {formatDate(ticketDetailQuery.data.updated_at)}
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="text-sm leading-7 text-slate-700">{ticketDetailQuery.data.ticket_text}</p>
                </div>
              </div>
            ) : (
              <EmptyState
                title="Select a ticket"
                description="Choose a ticket from the queue or search results to inspect its full details."
              />
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

function priorityTone(priority: string): "neutral" | "success" | "warning" | "danger" | "accent" {
  const normalized = priority.toLowerCase();

  if (normalized.includes("high") || normalized.includes("urgent")) {
    return "danger";
  }

  if (normalized.includes("medium")) {
    return "warning";
  }

  if (normalized.includes("low")) {
    return "success";
  }

  return "neutral";
}
