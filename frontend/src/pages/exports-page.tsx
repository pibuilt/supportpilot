import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { useAuth } from "@/features/auth/auth-context";
import { exportsApi } from "@/lib/api";
import { downloadBlob } from "@/lib/utils";
import { useToast } from "@/lib/toast";

const exportKinds = [
  { key: "documents", title: "Documents", description: "Document IDs, chunk counts, and embedding metadata." },
  { key: "sessions", title: "Sessions", description: "Session metadata with conversation content." },
  { key: "analyses", title: "Analyses", description: "Clause findings and contract analysis records." },
] as const;

export function ExportsPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const analysesPreview = useQuery({
    queryKey: ["analyses-preview"],
    queryFn: () => exportsApi.preview<Array<Record<string, unknown>>>("analyses"),
    enabled: hasApiKey,
  });

  async function handleDownload(kind: (typeof exportKinds)[number]["key"], format: "json" | "csv") {
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before exporting data" });
      return;
    }
    const payload = await exportsApi.download(kind, format);
    downloadBlob(payload.blob, payload.filename);
    push({ tone: "success", title: `${kind} export downloaded`, description: `Saved ${format.toUpperCase()} export.` });
  }

  return (
    <div className="space-y-6">
      {!hasApiKey ? (
        <EmptyState
          title="Product API key required"
          description="Export routes are protected by `x-api-key`. Add a valid product API key to enable downloads."
        />
      ) : null}
      <div className="grid gap-4 md:grid-cols-3">
        {exportKinds.map((item) => (
          <Card key={item.key}>
            <h3 className="text-lg font-semibold text-slate-950">{item.title}</h3>
            <p className="mt-2 text-sm text-slate-500">{item.description}</p>
            <div className="mt-5 flex gap-2">
              <Button type="button" variant="secondary" onClick={() => handleDownload(item.key, "json")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                JSON
              </Button>
              <Button type="button" variant="secondary" onClick={() => handleDownload(item.key, "csv")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                CSV
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <h3 className="text-lg font-semibold text-slate-950">Analysis export preview</h3>
        <p className="mt-1 text-sm text-slate-500">A lightweight view of the JSON export payload currently available from the backend.</p>
        <pre className="mt-4 max-h-[28rem] overflow-auto rounded-3xl bg-[#132029] p-5 text-sm text-white">
          {analysesPreview.isLoading
            ? "Loading preview..."
            : JSON.stringify((analysesPreview.data ?? []).slice(0, 5), null, 2)}
        </pre>
      </Card>
    </div>
  );
}
