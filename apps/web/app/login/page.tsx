"use client";

import { useState, type FormEvent } from "react";
import { Gauge, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [registering, setRegistering] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function request(path: string, body: object) {
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail ?? "Não foi possível autenticar.");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (registering) {
        await request("/auth/register", { name, email, password });
      }
      await request("/auth/login", { email, password });
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha de autenticação.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-6 text-ink">
      <section className="w-full max-w-md border border-line bg-white p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded bg-ink text-white">
            <Gauge size={21} aria-hidden="true" />
          </div>
          <div>
            <h1 className="font-semibold">Vena_IA Platform</h1>
            <p className="text-xs text-steel">Sessão segura v0.4.1</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 grid gap-3">
          {registering && (
            <input
              required
              maxLength={255}
              placeholder="Nome"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="rounded border border-line px-3 py-2 text-sm"
            />
          )}
          <input
            required
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="rounded border border-line px-3 py-2 text-sm"
          />
          <input
            required
            type="password"
            minLength={12}
            maxLength={128}
            autoComplete={registering ? "new-password" : "current-password"}
            placeholder="Senha"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="rounded border border-line px-3 py-2 text-sm"
          />
          {error && (
            <p className="border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center justify-center gap-2 rounded bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {submitting && <Loader2 size={16} className="animate-spin" aria-hidden="true" />}
            {registering ? "Criar conta" : "Entrar"}
          </button>
        </form>

        <button
          type="button"
          onClick={() => {
            setRegistering((current) => !current);
            setError(null);
          }}
          className="mt-4 text-sm text-machine underline"
        >
          {registering ? "Já tenho uma conta" : "Criar uma conta"}
        </button>
      </section>
    </main>
  );
}
