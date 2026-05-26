import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { adminApi } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { useToast } from "@/lib/toast";

export function AdminPage() {
  const { user } = useAuth();
  const { push } = useToast();
  const queryClient = useQueryClient();
  const [apiKeyId, setApiKeyId] = useState("");
  const [regeneratedKey, setRegeneratedKey] = useState("");

  const usersQuery = useQuery({
    queryKey: ["admin-users"],
    queryFn: adminApi.listUsers,
    enabled: user?.role === "admin" || user?.role === "root_admin",
  });

  const actionMutation = useMutation({
    mutationFn: async ({
      action,
      targetId,
    }: {
      action:
        | "suspend"
        | "activate"
        | "promote"
        | "demote"
        | "revoke-key"
        | "regenerate-key";
      targetId: string;
    }) => {
      if (action === "suspend") return adminApi.suspendUser(targetId);
      if (action === "activate") return adminApi.activateUser(targetId);
      if (action === "promote") return adminApi.promoteUser(targetId);
      if (action === "demote") return adminApi.demoteUser(targetId);
      if (action === "revoke-key") return adminApi.revokeApiKey(targetId);
      return adminApi.regenerateApiKey(targetId);
    },
    onSuccess: (data) => {
      if ("new_api_key" in data && typeof data.new_api_key === "string") {
        setRegeneratedKey(data.new_api_key);
      }
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      push({ tone: "success", title: data.message });
    },
    onError: () => {
      push({ tone: "error", title: "Admin action failed" });
    },
  });

  if (user?.role !== "admin" && user?.role !== "root_admin") {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="space-y-6">
      <Card>
        <h3 className="text-lg font-semibold text-slate-950">Tenant users</h3>
        <p className="mt-1 text-sm text-slate-500">
          These controls map directly to `/v1/admin/users/*` routes. Promotion and demotion are root-admin only.
        </p>
        <div className="mt-5 space-y-3">
          {usersQuery.data?.length ? (
            usersQuery.data.map((entry) => (
              <div key={entry.user_id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-semibold text-slate-900">{entry.full_name}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {entry.email} • {entry.role} • {entry.is_active ? "active" : "suspended"}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => actionMutation.mutate({ action: entry.is_active ? "suspend" : "activate", targetId: entry.user_id })}
                    >
                      {entry.is_active ? "Suspend" : "Activate"}
                    </Button>
                    {user.role === "root_admin" && entry.role === "user" ? (
                      <Button type="button" variant="secondary" onClick={() => actionMutation.mutate({ action: "promote", targetId: entry.user_id })}>
                        Promote
                      </Button>
                    ) : null}
                    {user.role === "root_admin" && entry.role === "admin" ? (
                      <Button type="button" variant="secondary" onClick={() => actionMutation.mutate({ action: "demote", targetId: entry.user_id })}>
                        Demote
                      </Button>
                    ) : null}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState title="No users returned" description="If this tenant has users, they will appear here once the admin query resolves." />
          )}
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-slate-950">Manual API key admin actions</h3>
        <p className="mt-1 text-sm text-slate-500">
          The backend supports revoke and regenerate by API key ID, but it does not currently expose an API key listing endpoint.
        </p>
        <div className="mt-5 flex flex-col gap-3 md:flex-row">
          <Input value={apiKeyId} onChange={(event) => setApiKeyId(event.target.value)} placeholder="API key ID" />
          <Button type="button" variant="secondary" onClick={() => actionMutation.mutate({ action: "revoke-key", targetId: apiKeyId })}>
            Revoke
          </Button>
          <Button type="button" onClick={() => actionMutation.mutate({ action: "regenerate-key", targetId: apiKeyId })}>
            Regenerate
          </Button>
        </div>
        {regeneratedKey ? (
          <div className="mt-4 rounded-2xl bg-slate-950 p-4 font-mono text-sm text-white">{regeneratedKey}</div>
        ) : null}
      </Card>
    </div>
  );
}
