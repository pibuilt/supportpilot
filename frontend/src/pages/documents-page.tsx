import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, FileUp, LoaderCircle, Trash2 } from "lucide-react";
import { AxiosError } from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { documentsApi, exportsApi } from "@/lib/api";
import { useJobPolling } from "@/hooks/use-job-polling";
import { downloadBlob, formatDate } from "@/lib/utils";
import { useToast } from "@/lib/toast";
import { useAuth } from "@/features/auth/auth-context";

export function DocumentsPage() {
  const { hasApiKey } = useAuth();
  const { push } = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [documentId, setDocumentId] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    enabled: hasApiKey,
  });
  const detailsQuery = useQuery({
    queryKey: ["document", selectedDocumentId],
    queryFn: () => documentsApi.get(selectedDocumentId!),
    enabled: hasApiKey && Boolean(selectedDocumentId),
  });
  const activeJobQuery = useJobPolling(activeJobId);

  const uploadMutation = useMutation({
    mutationFn: documentsApi.uploadFile,
    onSuccess: (data) => {
      setActiveJobId(data.job_id);
      push({
        tone: "info",
        title: "Ingestion queued",
        description: `Document ${documentId} is now being processed.`,
      });
    },
    onError: (error) => {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Upload failed";
      push({ tone: "error", title: "Unable to upload document", description: String(message) });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: documentsApi.remove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      if (selectedDocumentId) {
        queryClient.invalidateQueries({ queryKey: ["document", selectedDocumentId] });
      }
      push({ tone: "success", title: "Document deleted" });
    },
    onError: () => {
      push({ tone: "error", title: "Unable to delete document" });
    },
  });

  const ingestStatus = useMemo(() => activeJobQuery.data?.status ?? null, [activeJobQuery.data?.status]);

  useEffect(() => {
    if (activeJobQuery.data?.status === "COMPLETED") {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    }
  }, [activeJobQuery.data?.status, queryClient]);

  function onFilePicked(file: File | null) {
    setSelectedFile(file);
    if (file && !documentId) {
      setDocumentId(file.name.replace(/\.[^/.]+$/, "").replace(/\s+/g, "-").toLowerCase());
    }
  }

  async function handleUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before uploading" });
      return;
    }

    if (!selectedFile || !documentId) {
      push({ tone: "error", title: "Choose a file and document ID first" });
      return;
    }

    await uploadMutation.mutateAsync({
      documentId,
      file: selectedFile,
      onUploadProgress: setUploadProgress,
    });
  }

  async function handleExport(format: "json" | "csv") {
    if (!hasApiKey) {
      push({ tone: "error", title: "Add a product API key before exporting documents" });
      return;
    }

    const payload = await exportsApi.download("documents", format);
    downloadBlob(payload.blob, payload.filename);
    push({ tone: "success", title: `Documents exported as ${format.toUpperCase()}` });
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div className="space-y-6">
        {!hasApiKey ? (
          <EmptyState
            title="Product API key required"
            description="Upload, document listing, and ingestion polling are disabled until you restore a valid API key."
          />
        ) : null}
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Ingest document</h3>
              <p className="mt-1 text-sm text-slate-500">
                Upload supported files to `/v1/ingest/file` and poll `/v1/jobs/:job_id` until completion.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button type="button" variant="secondary" onClick={() => handleExport("json")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                Export JSON
              </Button>
              <Button type="button" variant="secondary" onClick={() => handleExport("csv")} disabled={!hasApiKey}>
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
              <Badge tone="accent">Async jobs</Badge>
            </div>
          </div>
          <form className="mt-5 space-y-4" onSubmit={handleUpload}>
            <div
              className="rounded-[28px] border border-dashed border-slate-300 bg-slate-50 p-6 text-center"
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                onFilePicked(event.dataTransfer.files[0] ?? null);
              }}
            >
              <FileUp className="mx-auto h-8 w-8 text-slate-400" />
              <p className="mt-3 text-sm font-medium text-slate-900">
                {selectedFile ? selectedFile.name : "Drag and drop a file here"}
              </p>
              <p className="mt-1 text-sm text-slate-500">PDF, DOCX, TXT, HTML, CSV, and Markdown depend on backend processors.</p>
              <Button className="mt-4" type="button" variant="secondary" onClick={() => fileInputRef.current?.click()}>
                Browse files
              </Button>
              <input
                ref={fileInputRef}
                className="hidden"
                type="file"
                onChange={(event) => onFilePicked(event.target.files?.[0] ?? null)}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Document ID</label>
              <Input value={documentId} onChange={(event) => setDocumentId(event.target.value)} placeholder="msa-2026-001" />
            </div>
            {uploadMutation.isPending ? (
              <div className="rounded-2xl bg-slate-100 p-3">
                <div className="flex items-center justify-between text-sm text-slate-600">
                  <span>Upload progress</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-white">
                  <div className="h-2 rounded-full bg-slate-900 transition-all" style={{ width: `${uploadProgress}%` }} />
                </div>
              </div>
            ) : null}
            <Button type="submit" disabled={uploadMutation.isPending || !hasApiKey}>
              {uploadMutation.isPending ? "Uploading..." : "Upload and ingest"}
            </Button>
          </form>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Document library</h3>
              <p className="mt-1 text-sm text-slate-500">List, inspect, and delete embedded document collections.</p>
            </div>
          </div>
          <div className="mt-5 space-y-3">
            {!hasApiKey ? (
              <EmptyState
                title="No API key available"
                description="Open the API Keys page and store a valid product API key to load documents."
              />
            ) : documentsQuery.isLoading ? (
              <>
                <Skeleton className="h-20" />
                <Skeleton className="h-20" />
              </>
            ) : documentsQuery.data?.length ? (
              documentsQuery.data.map((document) => (
                <div
                  key={document.document_id}
                  className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 md:flex-row md:items-center md:justify-between"
                >
                  <button
                    className="min-w-0 text-left"
                    onClick={() => setSelectedDocumentId(document.document_id)}
                    type="button"
                  >
                    <p className="truncate font-semibold text-slate-900">{document.document_id}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {document.chunk_count} chunks • {document.embedding_model}
                    </p>
                  </button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => deleteMutation.mutate(document.document_id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </Button>
                </div>
              ))
            ) : (
              <EmptyState title="No documents yet" description="Upload your first contract or support reference file to start retrieval." />
            )}
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <h3 className="text-lg font-semibold text-slate-950">Ingestion status</h3>
          <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            {activeJobId ? (
              <>
                <div className="flex items-center gap-3">
                  {activeJobQuery.isFetching ? <LoaderCircle className="h-4 w-4 animate-spin text-slate-400" /> : null}
                  <Badge
                    tone={
                      ingestStatus === "COMPLETED"
                        ? "success"
                        : ingestStatus === "FAILED" || ingestStatus === "DEAD_LETTER"
                          ? "danger"
                          : "warning"
                    }
                  >
                    {ingestStatus ?? "Queued"}
                  </Badge>
                </div>
                <p className="mt-3 text-sm text-slate-600">Job ID: {activeJobId}</p>
                <p className="mt-2 text-sm text-slate-500">
                  Started {formatDate(activeJobQuery.data?.started_at ?? undefined)}
                </p>
                {activeJobQuery.data?.error_message ? (
                  <p className="mt-3 rounded-2xl bg-rose-50 px-3 py-2 text-sm text-rose-800">
                    {activeJobQuery.data.error_message}
                  </p>
                ) : null}
              </>
            ) : (
              <p className="text-sm text-slate-500">No active ingestion job. Start by uploading a document.</p>
            )}
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-slate-950">Document details</h3>
          <div className="mt-4">
            {detailsQuery.isLoading ? (
              <Skeleton className="h-64" />
            ) : detailsQuery.data ? (
              <div className="space-y-4">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="font-semibold text-slate-900">{detailsQuery.data.document_id}</p>
                  <p className="mt-2 text-sm text-slate-500">
                    {detailsQuery.data.chunk_count} chunks • {detailsQuery.data.embedding_model} • version{" "}
                    {detailsQuery.data.embedding_version}
                  </p>
                </div>
                <div className="max-h-[32rem] space-y-3 overflow-auto pr-1">
                  {detailsQuery.data.chunks.slice(0, 12).map((chunk) => (
                    <div key={chunk.chunk_id} className="rounded-2xl border border-slate-200 bg-white p-4">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{chunk.chunk_id}</p>
                      <p className="mt-2 text-sm leading-6 text-slate-700">{chunk.chunk_text}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <EmptyState title="Select a document" description="Choose a row from the document list to inspect extracted chunks." />
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
