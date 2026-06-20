import { useMemo, useState } from "react";
import { Copy, KeyRound, LogOut, RefreshCw, ShieldCheck, Trash2 } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/features/auth/auth-context";
import { clearApiKeyStorage, setApiKey } from "@/lib/storage";
import { apiKeysApi } from "@/lib/api";
import { maskSecret } from "@/lib/utils";
import { useToast } from "@/lib/toast";

export function ApiKeysPage() {
  const { apiKey, user, validateApiKey, logout } = useAuth();
  const { push } = useToast();
  const queryClient = useQueryClient();
  const [manualApiKey, setManualApiKey] = useState("");
  const [issuedKey, setIssuedKey] = useState<string | null>(null);

  const validateMutation = useMutation({
    mutationFn: validateApiKey,
    onSuccess: (isValid) => {
      push({
        tone: isValid ? "success" : "error",
        title: isValid ? "API key is valid" : "API key is invalid",
      });
    },
  });

  const keysQuery = useQuery({
    queryKey: ["my-api-keys"],
    queryFn: apiKeysApi.listMine,
    enabled: Boolean(user),
  });

  const createMutation = useMutation({
    mutationFn: apiKeysApi.create,
    onSuccess: (data) => {
      setIssuedKey(data.api_key);
      queryClient.invalidateQueries({ queryKey: ["my-api-keys"] });
      push({ tone: "success", title: "New API key issued" });
    },
  });

  const actionMutation = useMutation({
    mutationFn: async ({
      action,
      apiKeyId,
    }: {
      action: "revoke" | "regenerate";
      apiKeyId: string;
    }) => {
      if (action === "revoke") {
        return apiKeysApi.revoke(apiKeyId);
      }
      return apiKeysApi.regenerate(apiKeyId);
    },
    onSuccess: (data) => {
      if ("api_key" in data) {
        setIssuedKey(data.api_key);
      }
      queryClient.invalidateQueries({ queryKey: ["my-api-keys"] });
      push({ tone: "success", title: "API key updated" });
    },
  });

  const activeKeyCount = useMemo(
    () => keysQuery.data?.filter((entry) => entry.is_active).length ?? 0,
    [keysQuery.data],
  );

  function handleCopy() {
    if (!apiKey) {
      return;
    }

    navigator.clipboard.writeText(apiKey);
    push({ tone: "success", title: "API key copied" });
  }

  function saveManualKey() {
    if (!manualApiKey.trim()) {
      push({ tone: "error", title: "Paste an API key first" });
      return;
    }

    setApiKey(manualApiKey.trim());
    push({ tone: "success", title: "API key stored locally" });
    window.location.reload();
  }

  function clearStoredKey() {
    clearApiKeyStorage();
    push({ tone: "success", title: "Stored API key removed" });
    window.location.reload();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <Card>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Current product API key</h3>
            <p className="mt-1 text-sm text-slate-500">
              Signed-in product routes can use your bearer session automatically. Store an API key locally only when you want this browser to use one explicitly.
            </p>
          </div>
          <KeyRound className="h-5 w-5 text-slate-400" />
        </div>
        <div className="mt-5 rounded-3xl bg-slate-950 p-5 text-white">
          <p className="text-xs uppercase tracking-[0.24em] text-white/45">Stored key</p>
          <p className="mt-3 font-mono text-sm">{apiKey ? maskSecret(apiKey, 8) : "No API key stored locally"}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge tone={apiKey ? "success" : "accent"}>{apiKey ? "Stored locally" : "Bearer fallback active"}</Badge>
            <Badge tone="neutral">{user?.tenant_id}</Badge>
            <Badge tone="neutral">{activeKeyCount} active key{activeKeyCount === 1 ? "" : "s"}</Badge>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <Button type="button" variant="secondary" onClick={handleCopy} disabled={!apiKey}>
            <Copy className="mr-2 h-4 w-4" />
            Copy
          </Button>
          <Button type="button" variant="secondary" onClick={() => validateMutation.mutate()}>
            <ShieldCheck className="mr-2 h-4 w-4" />
            Validate current key
          </Button>
          <Button type="button" variant="secondary" onClick={clearStoredKey} disabled={!apiKey}>
            <Trash2 className="mr-2 h-4 w-4" />
            Remove stored key
          </Button>
          <Button type="button" variant="danger" onClick={logout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
      </div>
      </Card>

      <Card>
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Manage API keys</h3>
            <p className="mt-1 text-sm text-slate-500">
              Issue, rotate, revoke, and locally store your product keys without leaving the dashboard.
            </p>
          </div>
          <Button type="button" variant="secondary" onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
            <KeyRound className="mr-2 h-4 w-4" />
            Issue new key
          </Button>
        </div>
        <div className="mt-5 space-y-3">
          {keysQuery.data?.length ? (
            keysQuery.data.map((entry) => (
              <div key={entry.api_key_id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-mono text-sm text-slate-900">{entry.key_prefix}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {entry.role} • {entry.is_active ? "active" : "revoked"} • {new Date(entry.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => actionMutation.mutate({ action: "regenerate", apiKeyId: entry.api_key_id })}
                    >
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Regenerate
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => actionMutation.mutate({ action: "revoke", apiKeyId: entry.api_key_id })}
                      disabled={!entry.is_active}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Revoke
                    </Button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
              No keys returned yet for this account.
            </div>
          )}
        </div>
        {issuedKey ? (
          <div className="mt-5 rounded-2xl bg-slate-950 p-4 text-white">
            <p className="text-xs uppercase tracking-[0.24em] text-white/45">Newest raw key</p>
            <p className="mt-3 break-all font-mono text-sm">{issuedKey}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button type="button" variant="secondary" onClick={() => navigator.clipboard.writeText(issuedKey)}>
                <Copy className="mr-2 h-4 w-4" />
                Copy raw key
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setApiKey(issuedKey);
                  push({ tone: "success", title: "Browser key updated" });
                  window.location.reload();
                }}
              >
                Store in this browser
              </Button>
            </div>
          </div>
        ) : null}
        <div className="mt-6 border-t border-slate-200 pt-6">
          <h4 className="text-base font-semibold text-slate-950">Recover a key locally</h4>
          <p className="mt-1 text-sm text-slate-500">
            Paste a previously issued key only if you need this browser to pin a specific credential.
          </p>
        </div>
        <div className="mt-5 space-y-3">
          <Input
            placeholder="Paste a previously issued API key"
            value={manualApiKey}
            onChange={(event) => setManualApiKey(event.target.value)}
          />
          <Button type="button" onClick={saveManualKey}>
            Store key in this browser
          </Button>
        </div>
      </Card>
    </div>
  );
}
