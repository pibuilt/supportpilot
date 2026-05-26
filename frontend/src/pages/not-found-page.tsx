import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="rounded-[28px] border border-white/60 bg-white/85 p-8 text-center shadow-panel backdrop-blur">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-400">404</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950">Page not found</h1>
        <p className="mt-3 text-sm text-slate-500">The requested route does not exist in this frontend shell.</p>
        <Link className="mt-6 inline-block rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white" to="/">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
