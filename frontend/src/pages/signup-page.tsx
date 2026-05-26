import { useState } from "react";
import { Link } from "react-router-dom";
import { AxiosError } from "axios";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/lib/toast";

export function SignupPage() {
  const { signup } = useAuth();
  const { push } = useToast();
  const [form, setForm] = useState({
    full_name: "",
    tenant_id: "",
    email: "",
    password: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      await signup(form);
      push({
        tone: "success",
        title: "Workspace created",
        description: "Your bearer token and first API key have been issued.",
      });
    } catch (error) {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Signup failed";
      push({ tone: "error", title: "Unable to sign up", description: String(message) });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div>
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Launch tenant</p>
      <h1 className="mt-3 text-3xl font-semibold text-slate-950">Create your SupportPilot account</h1>
      <p className="mt-3 text-sm text-slate-500">
        The first platform signup becomes `root_admin` according to the current backend bootstrap flow.
      </p>
      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Full name</label>
          <Input
            value={form.full_name}
            onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Tenant ID</label>
          <Input
            value={form.tenant_id}
            onChange={(event) => setForm((current) => ({ ...current, tenant_id: event.target.value }))}
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
          <Input
            value={form.email}
            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            type="email"
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
          <Input
            value={form.password}
            onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
            type="password"
            required
          />
        </div>
        <Button className="w-full" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating workspace..." : "Create account"}
        </Button>
      </form>
      <p className="mt-6 text-sm text-slate-500">
        Already set up?{" "}
        <Link className="font-semibold text-slate-900" to="/login">
          Sign in
        </Link>
      </p>
    </div>
  );
}
