"use client";

import Link from "next/link";
import { use, useCallback, useEffect, useState, type FormEvent } from "react";
import { FileText, Loader2, MessageSquareText, Upload } from "lucide-react";
import { useRouter } from "next/navigation";

import { api, ApiError } from "../../../lib/api";

type Project = { id: string; name: string; status: string };
type Document = {
  id: string;
  filename: string;
  status: string;
};
type DocumentList = { documents: Document[] };
type DocumentProcessingResponse = { document: Document };
type Evidence = {
  document_id: string;
  page_number: number;
  chunk_index: number;
  score: number;
  excerpt: string;
};
type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  evidence: Evidence[];
  error: string | null;
  created_at: string;
};
type AskResponse = { user_message: Message; assistant_message: Message };
type Report = {
  id: string;
  title: string;
  status: string;
  synthesis: string;
  evidence: Evidence[];
};

function describeError(error: unknown): string {
  if (!(error instanceof Error)) return "Falha inesperada.";
  if (error instanceof ApiError) {
    if (error.status === 401) return "Sua sessão expirou. Entre novamente.";
    if (error.status === 408) return "A API demorou demais para responder. Tente novamente.";
    if (error.status === 403) return "Você não possui permissão para executar esta ação.";
    if (error.status === 404) return "Recurso não encontrado ou sem acesso.";
    if (error.status === 409) return `A operação conflita com o estado atual: ${error.message}`;
    if (error.status === 422) return `Dados inválidos: ${error.message}`;
    if (error.status >= 500) return "Serviço temporariamente indisponível. Tente novamente.";
  }
  return error.message;
}

export default function ProjectPage({
  params
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = use(params);
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState<string | null>("load");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (signal?: AbortSignal) => {
    setError(null);
    const reportRequest = api<Report[]>(
      `/research/reports?project_id=${encodeURIComponent(projectId)}`,
      { signal }
    ).then(
      (data) => ({ ok: true as const, data }),
      (reason: unknown) => ({ ok: false as const, reason })
    );
    try {
      const [projectData, documentData, messageData] = await Promise.all([
        api<Project>(`/projects/${projectId}`, { signal }),
        api<DocumentList>(`/projects/${projectId}/documents`, { signal }),
        api<Message[]>(`/chat/${projectId}/messages`, { signal })
      ]);
      setProject(projectData);
      setDocuments(documentData.documents);
      setMessages(messageData);
      setBusy(null);

      const reportResult = await reportRequest;
      if (signal?.aborted) return;
      if (!reportResult.ok) {
        const reason = reportResult.reason;
        if (reason instanceof ApiError && reason.status === 401) throw reason;
        setReports([]);
        setError(`Projeto carregado, mas os relatórios não: ${describeError(reason)}`);
      } else {
        setReports(reportResult.data);
      }
    } catch (reason) {
      if (signal?.aborted) return;
      if (reason instanceof ApiError && reason.status === 401) {
        router.replace("/login");
        return;
      }
      setError(describeError(reason));
    } finally {
      if (!signal?.aborted) setBusy(null);
    }
  }, [projectId, router]);

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    return () => controller.abort();
  }, [load]);

  async function refreshDocuments() {
    const result = await api<DocumentList>(`/projects/${projectId}/documents`);
    setDocuments(result.documents);
  }

  async function refreshMessages() {
    setMessages(await api<Message[]>(`/chat/${projectId}/messages`));
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    const formElement = event.currentTarget;
    setBusy("upload");
    setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const created = await api<Document>(`/projects/${projectId}/documents`, {
        method: "POST",
        body: form
      });
      setDocuments((current) => [...current, created]);
      setFile(null);
      formElement.reset();
    } catch (reason) {
      setError(describeError(reason));
    } finally {
      setBusy(null);
    }
  }

  async function processDocument(document: Document) {
    setBusy(document.id);
    setError(null);
    try {
      if (document.status !== "READY") {
        const processed = await api<DocumentProcessingResponse>(
          `/documents/${document.id}/processing`,
          { method: "POST" }
        );
        setDocuments((current) =>
          current.map((item) =>
            item.id === processed.document.id ? processed.document : item
          )
        );
      }
      await api(`/documents/${document.id}/embeddings`, { method: "POST" });
    } catch (reason) {
      const operationError = describeError(reason);
      try {
        await refreshDocuments();
        setError(operationError);
      } catch (refreshReason) {
        setError(`${operationError} Estado não atualizado: ${describeError(refreshReason)}`);
      }
    } finally {
      setBusy(null);
    }
  }

  async function ask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("ask");
    setError(null);
    try {
      const result = await api<AskResponse>(`/chat/${projectId}/ask`, {
        method: "POST",
        body: JSON.stringify({ question })
      });
      setQuestion("");
      setMessages((current) => [
        ...current,
        result.user_message,
        result.assistant_message
      ]);
    } catch (reason) {
      const operationError = describeError(reason);
      try {
        await refreshMessages();
        setError(operationError);
      } catch (refreshReason) {
        setError(`${operationError} Histórico não atualizado: ${describeError(refreshReason)}`);
      }
    } finally {
      setBusy(null);
    }
  }

  async function createReport() {
    const lastAnswer = [...messages].reverse().find((message) => message.role === "assistant");
    if (!lastAnswer) {
      setError("Faça uma pergunta fundamentada antes de gerar o relatório.");
      return;
    }
    setBusy("report");
    setError(null);
    try {
      const created = await api<Report>("/research/reports", {
        method: "POST",
        body: JSON.stringify({
          project_id: projectId,
          report_type: "TECHNICAL_SYNTHESIS",
          title: `Relatório técnico — ${project?.name ?? "Projeto"}`,
          objective: "Registrar a síntese técnica fundamentada mais recente.",
          document_ids: [...new Set(lastAnswer.evidence.map((item) => item.document_id))],
          synthesis: lastAnswer.content,
          evidence: lastAnswer.evidence,
          limitations: [
            "Rascunho gerado com assistência de IA.",
            "As fontes e conclusões exigem revisão humana."
          ]
        })
      });
      setReports((current) => [...current, created]);
    } catch (reason) {
      setError(describeError(reason));
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="min-h-screen bg-surface px-6 py-6 text-ink">
      <div className="mx-auto grid max-w-6xl gap-6">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <Link href="/dashboard" className="text-sm text-machine underline">
              ← Projetos
            </Link>
            <h1 className="mt-2 text-2xl font-semibold">
              {project?.name ?? "Carregando projeto..."}
            </h1>
            <p className="text-sm text-steel">Fluxo integrado Vena_IA Platform v1.0</p>
          </div>
        </header>

        {error && (
          <div role="alert" className="border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <section className="grid gap-6 lg:grid-cols-2">
          <article className="border border-line bg-white p-5">
            <h2 className="flex items-center gap-2 font-semibold">
              <Upload size={18} /> Documentos PDF
            </h2>
            <form onSubmit={uploadDocument} className="mt-4 flex flex-wrap gap-2">
              <input
                required
                type="file"
                accept="application/pdf,.pdf"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                className="min-w-0 flex-1 rounded border border-line p-2 text-sm"
              />
              <button
                disabled={busy !== null || !file}
                className="rounded bg-ink px-4 py-2 text-sm text-white disabled:opacity-50"
              >
                Enviar
              </button>
            </form>
            <div className="mt-4 grid gap-2">
              {documents.length === 0 && !busy ? (
                <p className="text-sm text-steel">Nenhum documento enviado.</p>
              ) : (
                documents.map((document) => (
                  <div key={document.id} className="border border-line p-3 text-sm">
                    <div className="flex items-center justify-between gap-2">
                      <span className="flex min-w-0 items-center gap-2 font-medium">
                        <FileText size={16} />
                        <span className="truncate">{document.filename}</span>
                      </span>
                      <span className="text-xs text-steel">{document.status}</span>
                    </div>
                    {document.status !== "PROCESSING" && (
                      <button
                        type="button"
                        disabled={busy !== null}
                        onClick={() => void processDocument(document)}
                        className="mt-3 text-sm text-machine underline disabled:opacity-50"
                      >
                        {document.status === "READY"
                          ? "Indexar novamente"
                          : document.status === "FAILED"
                            ? "Tentar novamente"
                            : "Processar e indexar"}
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          </article>

          <article className="border border-line bg-white p-5">
            <h2 className="flex items-center gap-2 font-semibold">
              <MessageSquareText size={18} /> Conhecimento e histórico
            </h2>
            <div className="mt-4 max-h-96 space-y-3 overflow-y-auto">
              {messages.length === 0 ? (
                <p className="text-sm text-steel">
                  Processe um PDF e faça a primeira pergunta.
                </p>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`border p-3 text-sm ${
                      message.role === "assistant" ? "border-signal/40 bg-green-50" : "border-line"
                    }`}
                  >
                    <p className="text-xs font-semibold uppercase text-steel">
                      {message.role === "assistant" ? "Vena_IA" : "Você"} · {message.status}
                    </p>
                    <p className="mt-1 whitespace-pre-wrap">{message.content}</p>
                    {message.error && (
                      <p className="mt-2 border border-red-200 bg-red-50 p-2 text-xs text-red-700">
                        {message.error}
                      </p>
                    )}
                    {message.evidence.length > 0 && (
                      <ul className="mt-2 space-y-1 text-xs text-steel">
                        {message.evidence.map((source) => (
                          <li key={`${source.document_id}-${source.chunk_index}`}>
                            Fonte: doc {source.document_id.slice(0, 8)} · pág. {source.page_number} ·
                            chunk {source.chunk_index} · score {source.score.toFixed(3)}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))
              )}
            </div>
            <form onSubmit={ask} className="mt-4 grid gap-2">
              <textarea
                required
                maxLength={4000}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Pergunte somente sobre os documentos deste projeto"
                className="min-h-24 rounded border border-line p-3 text-sm"
              />
              <button
                disabled={busy !== null}
                className="flex items-center justify-center gap-2 rounded bg-ink px-4 py-2 text-sm text-white disabled:opacity-50"
              >
                {busy === "ask" && <Loader2 size={16} className="animate-spin" />}
                Perguntar com fontes
              </button>
            </form>
          </article>
        </section>

        <section className="border border-line bg-white p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-semibold">Relatórios técnicos iniciais</h2>
              <p className="text-sm text-steel">
                Rascunhos fundamentados que exigem revisão humana.
              </p>
            </div>
            <button
              type="button"
              onClick={() => void createReport()}
              disabled={busy !== null}
              className="rounded border border-line px-4 py-2 text-sm disabled:opacity-50"
            >
              Gerar do último resultado
            </button>
          </div>
          <div className="mt-4 grid gap-2">
            {reports.length === 0 ? (
              <p className="text-sm text-steel">Nenhum relatório gerado.</p>
            ) : (
              reports.map((report) => (
                <details key={report.id} className="border border-line p-3 text-sm">
                  <summary className="cursor-pointer font-medium">
                    {report.title} · {report.status}
                  </summary>
                  <p className="mt-3 whitespace-pre-wrap">{report.synthesis}</p>
                  <p className="mt-2 text-xs text-steel">
                    {report.evidence.length} fonte(s) rastreável(is)
                  </p>
                </details>
              ))
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
