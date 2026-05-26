import { useState } from "react";
import { Link } from "react-router-dom";
import { AxiosError } from "axios";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/lib/toast";

export function LoginPage() {
  const { login } = useAuth();
  const { push } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      await login({ email, password });
      push({ tone: "success", title: "Welcome back", description: "Your workspace is ready." });
    } catch (error) {
      const message = error instanceof AxiosError ? error.response?.data?.detail : "Login failed";
      push({ tone: "error", title: "Unable to login", description: String(message) });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div>
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">SupportPilot</p>
      <h1 className="mt-3 text-3xl font-semibold text-slate-950">Sign in to your workspace</h1>
      <p className="mt-3 text-sm text-slate-500">
        Product routes use your stored API key, while admin and identity routes use JWT bearer auth.
      </p>

      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
          <Input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
          <Input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            required
          />
        </div>
        <Button className="w-full" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>

      <p className="mt-6 text-sm text-slate-500">
        New tenant?{" "}
        <Link className="font-semibold text-slate-900" to="/signup">
          Create an account
        </Link>
      </p>
    </div>
  );
}
