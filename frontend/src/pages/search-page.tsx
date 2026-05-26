import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { AxiosError } from "axios";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useAuth } from "@/features/auth/auth-context";
import { documentsApi, searchApi } from "@/lib/api";
import { useToast } from "@/lib/toast";

export function SearchPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    enabled: hasApiKey,
  });
  const [query, setQuery] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [topK, setTopK] = useState(5);

  const searchMutation = useMutation({
    mutationFn: searchApi.run,
    onError: (error) => {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Search failed";
      push({ tone: "error", title: "Unable to search", description: String(message) });
    },
  });

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before searching" });
      return;
    }
    await searchMutation.mutateAsync({
      query,
      document_id: documentId || undefined,
      top_k: topK,
    });
  }

  return (
    <div className="space-y-6">
      <Card>
        {!hasApiKey ? (
          <div className="mb-5">
            <EmptyState
              title="Product API key required"
              description="Semantic search is available after you store a valid product API key."
            />
          </div>
        ) : null}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Semantic search</h3>
            <p className="mt-1 text-sm text-slate-500">Query embedded documents with optional document scoping.</p>
          </div>
          <Badge tone="accent">RAG retrieval</Badge>
        </div>
        <form className="mt-5 grid gap-4 md:grid-cols-[1.4fr_0.8fr_0.4fr_auto]" onSubmit={handleSubmit}>
          <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search for liability caps, SLAs, termination rights..." required />
          <Select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
            <option value="">All documents</option>
            {documentsQuery.data?.map((document) => (
              <option key={document.document_id} value={document.document_id}>
                {document.document_id}
              </option>
            ))}
          </Select>
          <Input min={1} max={20} type="number" value={topK} onChange={(event) => setTopK(Number(event.target.value))} />
          <Button type="submit" disabled={searchMutation.isPending || !hasApiKey}>
            <Search className="mr-2 h-4 w-4" />
            {searchMutation.isPending ? "Searching..." : "Search"}
          </Button>
        </form>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-slate-950">Results</h3>
        <div className="mt-5 space-y-3">
          {searchMutation.data?.results.length ? (
            searchMutation.data.results.map((result) => (
              <div key={`${result.document_id}-${result.chunk_id}`} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="neutral">{result.document_id}</Badge>
                  <Badge tone="accent">Chunk {result.chunk_id.slice(0, 8)}</Badge>
                  <Badge tone="success">Score {result.score.toFixed(3)}</Badge>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-700">{result.chunk_text || result.preview}</p>
              </div>
            ))
          ) : searchMutation.isPending ? (
            <p className="text-sm text-slate-500">Running retrieval pipeline...</p>
          ) : (
            <EmptyState title="No search results yet" description="Run a query to inspect semantic matches and previews." />
          )}
        </div>
      </Card>
    </div>
  );
}
