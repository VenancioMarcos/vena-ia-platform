"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Boxes, Gauge, Loader2, LogOut, Plus } from "lucide-react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Project = {
  id: string;
  name: string;
  status: string;
  owner_id: string;
  created_at: string;
};

class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number
  ) {
    super(message);
  }
}

async function fetchJson<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(
      body.detail ?? `Request failed with status ${response.status}`,
      response.status
    );
  }
  return response.json() as Promise<T>;
}

export default function Dashboard() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [projectName, setProjectName] = useState("");

  async function loadProjects() {
    setLoading(true);
    setError(null);
    try {
      await fetchJson(`${API_URL}/auth/me`);
      setProjects(await fetchJson<Project[]>(`${API_URL}/projects`));
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }
      setError(
        err instanceof Error
          ? `Não foi possível conectar à API (${API_URL}): ${err.message}`
          : "Erro desconhecido ao carregar projetos."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadProjects();
    // loadProjects intentionally runs once for the current authenticated session.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await fetchJson<Project>(`${API_URL}/projects`, {
        method: "POST",
        body: JSON.stringify({ name: projectName })
      });
      setProjectName("");
      await loadProjects();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }
      setError(
        err instanceof ApiError && err.status === 403
          ? "Você não possui permissão para criar este recurso."
          : err instanceof Error
            ? err.message
            : "Erro ao criar projeto."
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleLogout() {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include"
    });
    router.replace("/login");
  }

  return (
    <main className="min-h-screen bg-surface text-ink">
      <section className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded border border-line bg-ink text-white">
              <Gauge size={21} aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm font-semibold leading-5">Vena_IA Platform</p>
              <p className="text-xs text-steel">Dashboard — v0.4.1 Security Gate</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => void handleLogout()}
            className="flex items-center gap-2 rounded border border-line px-3 py-2 text-sm"
          >
            <LogOut size={16} aria-hidden="true" />
            Sair
          </button>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-6 px-6 py-6">
        <div className="border border-line bg-white p-5">
          <h2 className="text-base font-semibold">Novo Projeto</h2>
          <p className="mt-1 text-xs text-steel">
            O proprietário é definido exclusivamente pela sessão autenticada.
          </p>
          <form onSubmit={handleCreateProject} className="mt-4 grid gap-3">
            <input
              required
              placeholder="Nome do projeto"
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              className="rounded border border-line px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center justify-center gap-2 rounded bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              {submitting ? (
                <Loader2 size={16} className="animate-spin" aria-hidden="true" />
              ) : (
                <Plus size={16} aria-hidden="true" />
              )}
              Criar projeto
            </button>
          </form>
        </div>

        {error && (
          <div className="border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="border border-line bg-white p-5">
          <h2 className="flex items-center gap-2 text-base font-semibold">
            <Boxes size={18} aria-hidden="true" />
            Projetos ({projects.length})
          </h2>

          {loading ? (
            <p className="mt-4 text-sm text-steel">Carregando...</p>
          ) : projects.length === 0 ? (
            <p className="mt-4 text-sm text-steel">
              Nenhum projeto ainda. Crie o primeiro no formulário acima.
            </p>
          ) : (
            <ul className="mt-4 grid gap-2">
              {projects.map((project) => (
                <li
                  key={project.id}
                  className="flex items-center justify-between border border-line px-4 py-3 text-sm"
                >
                  <span className="font-medium">{project.name}</span>
                  <span className="text-xs text-steel">{project.status}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </main>
  );
}
