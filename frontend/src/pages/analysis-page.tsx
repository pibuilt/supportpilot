import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AlertTriangle, Download } from "lucide-react";
import { AxiosError } from "axios";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Select } from "@/components/ui/select";
import { useAuth } from "@/features/auth/auth-context";
import { analysisApi, documentsApi, exportsApi } from "@/lib/api";
import { downloadBlob } from "@/lib/utils";
import { useToast } from "@/lib/toast";

export function AnalysisPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    enabled: hasApiKey,
  });
  const [documentId, setDocumentId] = useState("");

  const analysisMutation = useMutation({
    mutationFn: analysisApi.run,
    onError: (error) => {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Analysis failed";
      push({ tone: "error", title: "Unable to analyze contract", description: String(message) });
    },
  });

  async function exportAnalyses(format: "json" | "csv") {
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before exporting analyses" });
      return;
    }
    const payload = await exportsApi.download("analyses", format);
    downloadBlob(payload.blob, payload.filename);
  }

  return (
    <div className="space-y-6">
      {!hasApiKey ? (
        <EmptyState
          title="Product API key required"
          description="Contract analysis depends on product API authentication. Add your key from the API Keys page."
        />
      ) : null}
      <Card>
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Contract analysis</h3>
            <p className="mt-1 text-sm text-slate-500">Run clause extraction and risk summarization on an ingested document.</p>
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="secondary" onClick={() => exportAnalyses("json")}>
              <Download className="mr-2 h-4 w-4" />
              Export JSON
            </Button>
            <Button type="button" variant="secondary" onClick={() => exportAnalyses("csv")}>
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </div>
        <div className="mt-5 flex flex-col gap-4 md:flex-row">
          <Select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
            <option value="">Select a document</option>
            {documentsQuery.data?.map((document) => (
              <option key={document.document_id} value={document.document_id}>
                {document.document_id}
              </option>
            ))}
          </Select>
          <Button
            type="button"
            onClick={() => analysisMutation.mutate(documentId)}
            disabled={!documentId || analysisMutation.isPending || !hasApiKey}
          >
            {analysisMutation.isPending ? "Analyzing..." : "Analyze document"}
          </Button>
        </div>
      </Card>

      {analysisMutation.data ? (
        <div className="grid gap-6 xl:grid-cols-[0.75fr_1.25fr]">
          <Card>
            <h3 className="text-lg font-semibold text-slate-950">Executive summary</h3>
            <div className="mt-4 grid gap-3">
              <SummaryRow label="Overall risk" value={analysisMutation.data.executive_summary?.overall_risk ?? "unknown"} />
              <SummaryRow label="Total clauses" value={String(analysisMutation.data.summary.total_clauses)} />
              <SummaryRow label="High risk" value={String(analysisMutation.data.executive_summary?.high_risk_count ?? 0)} />
              <SummaryRow label="Medium risk" value={String(analysisMutation.data.executive_summary?.medium_risk_count ?? 0)} />
              <SummaryRow label="Low risk" value={String(analysisMutation.data.executive_summary?.low_risk_count ?? 0)} />
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold text-slate-950">Clause findings</h3>
            <div className="mt-4 space-y-3">
              {analysisMutation.data.clauses.map((clause, index) => (
                <div key={`${clause.clause_type}-${index}`} className="rounded-2xl border border-slate-200 bg-white p-4">
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
                    <Badge tone="accent">Confidence {clause.confidence_score.toFixed(2)}</Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-700">{clause.matched_text}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      ) : (
        <EmptyState title="No analysis yet" description="Select an ingested document and run analysis to inspect extracted clauses and risks." />
      )}
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}
