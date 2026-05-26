import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/layout/protected-route";
import { AppShell } from "@/components/layout/app-shell";
import { AuthLayout } from "@/pages/auth-layout";
import { LoginPage } from "@/pages/login-page";
import { SignupPage } from "@/pages/signup-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { DocumentsPage } from "@/pages/documents-page";
import { TicketsPage } from "@/pages/tickets-page";
import { AssistantPage } from "@/pages/assistant-page";
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
          { path: "/search", element: <Navigate to="/assistant?mode=search" replace /> },
          { path: "/analysis", element: <Navigate to="/assistant?mode=analyze" replace /> },
          { path: "/tickets", element: <TicketsPage /> },
          { path: "/assistant", element: <AssistantPage /> },
          { path: "/sessions", element: <Navigate to="/assistant" replace /> },
          { path: "/exports", element: <Navigate to="/assistant" replace /> },
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
