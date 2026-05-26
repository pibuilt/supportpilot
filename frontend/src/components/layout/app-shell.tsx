import { Bot, Files, LayoutDashboard, LogOut, Shield, Ticket } from "lucide-react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useMemo } from "react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const labels: Record<string, string> = {
  "": "Dashboard",
  documents: "Documents",
  tickets: "Tickets",
  assistant: "AI Assistant",
  "api-keys": "API Keys",
  admin: "Admin",
};

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user, hasApiKey } = useAuth();

  const items = useMemo(
    () => [
      { to: "/", label: "Dashboard", icon: LayoutDashboard },
      { to: "/documents", label: "Documents", icon: Files },
      { to: "/tickets", label: "Tickets", icon: Ticket },
      { to: "/assistant", label: "Assistant", icon: Bot },
      { to: "/api-keys", label: "API Keys", icon: Shield },
    ],
    [],
  );

  const breadcrumbs = location.pathname
    .split("/")
    .filter(Boolean)
    .map((segment) => labels[segment] ?? segment);

  return (
    <div className="min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-[1600px] gap-6 px-4 py-4 lg:px-6">
        <aside className="hidden w-72 shrink-0 flex-col rounded-[32px] border border-white/60 bg-[#132029] px-5 py-6 text-white shadow-panel lg:flex">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-white/50">SupportPilot</p>
            <h1 className="mt-3 text-2xl font-semibold">Operations cockpit</h1>
            <p className="mt-2 text-sm text-white/65">
              Manage ingestion, analysis, retrieval, and orchestration from one place.
            </p>
          </div>
          <nav className="mt-8 flex flex-1 flex-col gap-2">
            {items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                    isActive ? "bg-white/12 text-white" : "text-white/70 hover:bg-white/8 hover:text-white",
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
            {(user?.role === "admin" || user?.role === "root_admin") && (
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  cn(
                    "mt-2 flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                    isActive ? "bg-orange-500/20 text-orange-100" : "text-orange-100/75 hover:bg-orange-500/10",
                  )
                }
              >
                <Shield className="h-4 w-4" />
                Admin
              </NavLink>
            )}
          </nav>
          <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm font-semibold">{user?.full_name}</p>
            <p className="mt-1 text-xs text-white/60">{user?.email}</p>
            <div className="mt-3 flex items-center gap-2">
              <Badge tone="accent">{user?.role}</Badge>
              <Badge tone={hasApiKey ? "success" : "warning"}>{hasApiKey ? "API ready" : "API key missing"}</Badge>
            </div>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          <div className="glass-panel sticky top-4 z-10 rounded-[28px] border border-white/60 px-5 py-4 shadow-panel">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-slate-400">
                  {breadcrumbs.length > 0 ? breadcrumbs.join(" / ") : "Dashboard"}
                </p>
                <h2 className="mt-1 text-2xl font-semibold text-slate-950">
                  {breadcrumbs[breadcrumbs.length - 1] ?? "Dashboard"}
                </h2>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                {!hasApiKey && (
                  <button
                    className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-900"
                    onClick={() => navigate("/api-keys")}
                    type="button"
                  >
                    Product APIs need a stored API key
                  </button>
                )}
                <Button variant="secondary" onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
          <div className="mt-6 flex-1">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
