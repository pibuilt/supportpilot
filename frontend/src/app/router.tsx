import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/layout/protected-route";
import { AppShell } from "@/components/layout/app-shell";
import { AuthLayout } from "@/pages/auth-layout";
import { LoginPage } from "@/pages/login-page";
import { SignupPage } from "@/pages/signup-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { DocumentsPage } from "@/pages/documents-page";
import { SearchPage } from "@/pages/search-page";
import { AnalysisPage } from "@/pages/analysis-page";
import { TicketsPage } from "@/pages/tickets-page";
import { AssistantPage } from "@/pages/assistant-page";
import { SessionsPage } from "@/pages/sessions-page";
import { ExportsPage } from "@/pages/exports-page";
import { ApiKeysPage } from "@/pages/api-keys-page";
import { AdminPage } from "@/pages/admin-page";
import { AuthProvider } from "@/features/auth/auth-context";
import { NotFoundPage } from "@/pages/not-found-page";

function Providers({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

export const router = createBrowserRouter([
  {
    element: (
      <Providers>
        <ProtectedRoute />
      </Providers>
    ),
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/", element: <DashboardPage /> },
          { path: "/documents", element: <DocumentsPage /> },
          { path: "/search", element: <SearchPage /> },
          { path: "/analysis", element: <AnalysisPage /> },
          { path: "/tickets", element: <TicketsPage /> },
          { path: "/assistant", element: <AssistantPage /> },
          { path: "/sessions", element: <SessionsPage /> },
          { path: "/exports", element: <ExportsPage /> },
          { path: "/api-keys", element: <ApiKeysPage /> },
          { path: "/admin", element: <AdminPage /> },
        ],
      },
    ],
  },
  {
    element: (
      <Providers>
        <AuthLayout />
      </Providers>
    ),
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/signup", element: <SignupPage /> },
      { path: "*", element: <Navigate to="/login" replace /> },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
