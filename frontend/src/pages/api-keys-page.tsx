import { useState } from "react";
import { Copy, KeyRound, LogOut, ShieldCheck, Trash2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/features/auth/auth-context";
import { clearApiKeyStorage, setApiKey } from "@/lib/storage";
import { maskSecret } from "@/lib/utils";
import { useToast } from "@/lib/toast";

export function ApiKeysPage() {
  const { apiKey, user, validateApiKey, logout } = useAuth();
  const { push } = useToast();
  const [manualApiKey, setManualApiKey] = useState("");

  const validateMutation = useMutation({
    mutationFn: validateApiKey,
    onSuccess: (isValid) => {
      push({
        tone: isValid ? "success" : "error",
        title: isValid ? "API key is valid" : "API key is invalid",
      });
    },
  });

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
              Product routes require `x-api-key`. Fresh logins now rotate and return a usable key for this browser.
            </p>
          </div>
          <KeyRound className="h-5 w-5 text-slate-400" />
        </div>
        <div className="mt-5 rounded-3xl bg-slate-950 p-5 text-white">
          <p className="text-xs uppercase tracking-[0.24em] text-white/45">Stored key</p>
          <p className="mt-3 font-mono text-sm">{apiKey ? maskSecret(apiKey, 8) : "No API key stored locally"}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge tone={apiKey ? "success" : "warning"}>{apiKey ? "Ready" : "Missing"}</Badge>
            <Badge tone="neutral">{user?.tenant_id}</Badge>
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
        <h3 className="text-lg font-semibold text-slate-950">Recover a key locally</h3>
        <p className="mt-1 text-sm text-slate-500">
          You can still paste a previously issued key manually if you need to recover access in this browser.
        </p>
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
        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          The backend exposes validation, and login now rotates the active key. This page keeps the manual recovery flow for edge cases.
        </div>
      </Card>
    </div>
  );
}
