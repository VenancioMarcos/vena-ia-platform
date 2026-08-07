"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { AlertTriangle, Bot, CheckCircle2, CircleDashed, FlaskConical, GitBranch, ShieldCheck } from "lucide-react";

import { api } from "../lib/api";
import type {
  AssistanceProfile,
  CatalogItem,
  IntegratedWorkflow,
  SpecializedAssistance,
  WorkflowRequest
} from "../lib/engineering-contracts";

type DocumentReference = { id: string; filename: string; status: string };
type Props = { projectId: string; documents: DocumentReference[]; onError: (message: string) => void };
type Stage = { label: string; status: string; detail: string };

const profiles: AssistanceProfile[] = [
  "CAD_ANALYSIS",
  "MANUFACTURING_ENGINEERING",
  "RESEARCH",
  "DOCUMENTATION_REPORTING"
];

function stageClass(status: string): string {
  if (["AVAILABLE", "COMPLETE_PRELIMINARY"].includes(status)) return "border-signal/40 bg-green-50";
  if (status.startsWith("BLOCKED") || status === "FAILED") return "border-red-200 bg-red-50";
  return "border-amber-200 bg-amber-50";
}

function List({ title, values, empty = "Nenhum item." }: { title: string; values: string[]; empty?: string }) {
  return (
    <div>
      <h4 className="text-xs font-semibold uppercase tracking-wide text-steel">{title}</h4>
      {values.length === 0 ? <p className="mt-1 text-sm text-steel">{empty}</p> : (
        <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">{values.map((value) => <li key={value}>{value}</li>)}</ul>
      )}
    </div>
  );
}

export function EngineeringWorkspace({ projectId, documents, onError }: Props) {
  const [catalogs, setCatalogs] = useState<CatalogItem[]>([]);
  const [request, setRequest] = useState<WorkflowRequest>({ document_id: "", feature_id: "feature-0001" });
  const [workflow, setWorkflow] = useState<IntegratedWorkflow | null>(null);
  const [assistance, setAssistance] = useState<SpecializedAssistance | null>(null);
  const [profile, setProfile] = useState<AssistanceProfile>("CAD_ANALYSIS");
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState<"workflow" | "assistance" | null>(null);
  const [reviewAcknowledged, setReviewAcknowledged] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    api<CatalogItem[]>("/engineering/catalogs", { signal: controller.signal })
      .then(setCatalogs)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) onError(reason instanceof Error ? reason.message : "Falha ao carregar catálogos.");
      });
    return () => controller.abort();
  }, [onError]);

  const stages = useMemo<Stage[]>(() => {
    if (!workflow) return [
      { label: "CAD", status: "NOT_AVAILABLE", detail: "Execute o workflow para analisar o documento." },
      { label: "Features", status: "NOT_AVAILABLE", detail: "Sem análise de features." },
      { label: "Engineering", status: "NOT_AVAILABLE", detail: "Sem recomendação." },
      { label: "Process Planning", status: "NOT_AVAILABLE", detail: "Sem planejamento." },
      { label: "CNC Neutral", status: "NOT_AVAILABLE", detail: "Sem plano neutro." },
      { label: "Integrated Report", status: "NOT_AVAILABLE", detail: "Sem relatório integrado." }
    ];
    return [
      { label: "CAD", status: workflow.geometry.status, detail: `${workflow.geometry.schema_version} · topologia ${workflow.geometry.topology_valid === true ? "válida" : "não confirmada"}` },
      { label: "Features", status: workflow.features.status, detail: `${workflow.features.feature_count} feature(s) reconhecida(s)` },
      { label: "Engineering", status: workflow.engineering?.status ?? "NOT_AVAILABLE", detail: workflow.engineering?.compatibility ?? "Entradas insuficientes" },
      { label: "Process Planning", status: workflow.planning?.status ?? "NOT_AVAILABLE", detail: workflow.planning ? `${workflow.planning.planning_candidates.length} candidato(s)` : "Planejamento indisponível" },
      { label: "CNC Neutral", status: workflow.cnc_neutral_plan?.status ?? "NOT_AVAILABLE", detail: workflow.cnc_neutral_plan?.operation ?? "Plano neutro indisponível" },
      { label: "Integrated Report", status: workflow.integrated_report.conclusion, detail: workflow.integrated_report.schema_version }
    ];
  }, [workflow]);

  function setCatalog(kind: CatalogItem["kind"], id: string) {
    const key = kind === "MATERIAL" ? "material_id" : kind === "MACHINE" ? "machine_id" : "tool_id";
    setRequest((current) => ({ ...current, [key]: id || undefined }));
  }

  async function runWorkflow(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("workflow");
    setAssistance(null);
    setReviewAcknowledged(false);
    try {
      setWorkflow(await api<IntegratedWorkflow>("/engineering/workflows", { method: "POST", body: JSON.stringify(request) }));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha ao executar workflow.");
    } finally {
      setBusy(null);
    }
  }

  async function runAssistance(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workflow) return;
    setBusy("assistance");
    try {
      setAssistance(await api<SpecializedAssistance>("/engineering/workflow-assistance", {
        method: "POST",
        body: JSON.stringify({
          profile,
          question,
          workflow: request,
          ...(profile === "RESEARCH" ? { research_project_id: projectId } : {})
        })
      }));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha na assistência especializada.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <section aria-labelledby="engineering-title" className="border border-line bg-white p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="engineering-title" className="flex items-center gap-2 font-semibold"><GitBranch size={18} /> Workflow integrado de engenharia</h2>
          <p className="mt-1 text-sm text-steel">Resultados preliminares, não produtivos e sujeitos à revisão humana.</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold" aria-label="Restrições do workflow">
          <span className="border border-red-300 bg-red-50 px-2 py-1">NON_PRODUCTION</span>
          <span className="border border-amber-300 bg-amber-50 px-2 py-1">REQUIRES_HUMAN_REVIEW</span>
          <span className="border border-blue-300 bg-blue-50 px-2 py-1">CATALOG: GLOBAL AUTHENTICATED</span>
        </div>
      </div>

      <form onSubmit={runWorkflow} className="mt-5 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        <label className="grid gap-1 text-sm">Documento STEP
          <select required value={request.document_id} onChange={(event) => setRequest((current) => ({ ...current, document_id: event.target.value }))} className="rounded border border-line p-2">
            <option value="">Selecione</option>
            {documents.map((document) => <option key={document.id} value={document.id}>{document.filename} · {document.status}</option>)}
          </select>
        </label>
        <label className="grid gap-1 text-sm">Feature
          <input required pattern="feature-[0-9]{4}" value={request.feature_id} onChange={(event) => setRequest((current) => ({ ...current, feature_id: event.target.value }))} className="rounded border border-line p-2" />
        </label>
        {(["MATERIAL", "MACHINE", "TOOL"] as const).map((kind) => (
          <label key={kind} className="grid gap-1 text-sm">{kind[0] + kind.slice(1).toLowerCase()}
            <select onChange={(event) => setCatalog(kind, event.target.value)} className="rounded border border-line p-2">
              <option value="">Não informado</option>
              {catalogs.filter((item) => item.kind === kind).map((item) => <option key={item.id} value={item.id}>{item.code} · {item.name}</option>)}
            </select>
          </label>
        ))}
        <label className="grid gap-1 text-sm md:col-span-2">Intenção de manufatura
          <input maxLength={500} value={request.manufacturing_intent ?? ""} onChange={(event) => setRequest((current) => ({ ...current, manufacturing_intent: event.target.value || undefined }))} className="rounded border border-line p-2" placeholder="Opcional; não constitui autorização produtiva" />
        </label>
        <button disabled={busy !== null} className="self-end rounded bg-ink px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-signal disabled:opacity-50">
          {busy === "workflow" ? "Executando…" : "Executar workflow preliminar"}
        </button>
      </form>

      <div className="mt-5 grid gap-3 md:grid-cols-2 lg:grid-cols-3" aria-live="polite" aria-busy={busy === "workflow"}>
        {stages.map((stage, index) => (
          <article key={stage.label} className={`border p-3 ${stageClass(stage.status)}`}>
            <p className="text-xs font-semibold text-steel">ETAPA {index + 1}</p>
            <h3 className="font-semibold">{stage.label}</h3>
            <p className="mt-1 text-xs font-semibold">{stage.status}</p>
            <p className="mt-1 text-sm text-steel">{stage.detail}</p>
          </article>
        ))}
      </div>

      {workflow && (
        <div className="mt-6 grid gap-5">
          <div role="status" className={`border p-4 ${stageClass(workflow.workflow_status)}`}>
            <p className="text-xs font-semibold text-steel">STATUS GLOBAL DO BACKEND</p>
            <p className="font-semibold">{workflow.workflow_status}</p>
            <p className="mt-1 text-sm">COMPLETE_PRELIMINARY não significa produção.</p>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <List title="Entradas ausentes" values={workflow.missing_inputs} />
            <List title="Avisos" values={workflow.warnings} />
            <List title="Limitações" values={workflow.limitations} />
          </div>

          {workflow.cnc_neutral_plan && (
            <article className="border border-blue-200 bg-blue-50 p-4">
              <h3 className="font-semibold">Plano CNC neutro</h3>
              <p className="mt-1 text-sm">{workflow.cnc_neutral_plan.schema_version} · {workflow.cnc_neutral_plan.operation}</p>
              <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold">
                <span className="border border-blue-300 px-2 py-1">SIMULATION_ONLY</span>
                <span className="border border-blue-300 px-2 py-1">executable_output=false</span>
                <span className="border border-amber-300 px-2 py-1">{workflow.cnc_neutral_plan.review_status}</span>
              </div>
              <List title="Limitações CNC" values={workflow.cnc_neutral_plan.limitations} />
            </article>
          )}

          <article className="border border-line p-4">
            <h3 className="flex items-center gap-2 font-semibold"><ShieldCheck size={18} /> Revisão humana</h3>
            <p className="mt-1 text-sm text-steel">Reconhecer esta lista registra apenas estado visual local; não aprova fabricação.</p>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm">{workflow.integrated_report.human_review_checklist.map((item) => <li key={item}>{item}</li>)}</ul>
            <label className="mt-3 flex items-center gap-2 text-sm">
              <input type="checkbox" checked={reviewAcknowledged} onChange={(event) => setReviewAcknowledged(event.target.checked)} />
              {reviewAcknowledged ? "REVIEW ACKNOWLEDGED" : "REVIEW REQUIRED"}
            </label>
          </article>

          <form onSubmit={runAssistance} className="border border-violet-200 bg-violet-50 p-4">
            <h3 className="flex items-center gap-2 font-semibold"><Bot size={18} /> AI Assistance</h3>
            <p className="mt-1 text-sm">Separada do resultado determinístico acima. Não altera o workflow fonte.</p>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              <label className="grid gap-1 text-sm">Perfil
                <select value={profile} onChange={(event) => setProfile(event.target.value as AssistanceProfile)} className="rounded border border-line bg-white p-2">
                  {profiles.map((item) => <option key={item}>{item}</option>)}
                </select>
              </label>
              <label className="grid gap-1 text-sm md:col-span-2">Pergunta
                <textarea required minLength={3} maxLength={4000} value={question} onChange={(event) => setQuestion(event.target.value)} className="min-h-20 rounded border border-line bg-white p-2" />
              </label>
            </div>
            <button disabled={busy !== null} className="mt-3 rounded bg-violet-900 px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:opacity-50">
              {busy === "assistance" ? "Consultando…" : "Solicitar assistência para revisão"}
            </button>
          </form>

          {assistance && (
            <article className="border border-violet-200 p-4" aria-live="polite">
              <h3 className="font-semibold">AI ASSISTANCE · {assistance.assistance_status}</h3>
              <p className="mt-2 whitespace-pre-wrap text-sm">{assistance.response ?? "Nenhuma resposta disponível."}</p>
              <p className="mt-2 break-all text-xs text-steel">Deterministic input trace: {assistance.deterministic_input_trace}</p>
              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <List title="Evidências ausentes" values={assistance.missing_evidence} />
                <List title="Avisos" values={assistance.warnings} />
                <List title="Limitações" values={assistance.limitations} />
              </div>
              {assistance.profile === "RESEARCH" && (
                <div className="mt-4">
                  <h4 className="flex items-center gap-2 font-semibold"><FlaskConical size={16} /> Research grounding</h4>
                  <p className="text-sm text-steel">DOE = PRELIMINARY · ANOVA = DESCRIPTIVE ONLY</p>
                  {assistance.citations.length === 0 ? <p className="mt-2 text-sm text-steel">Sem citações disponíveis.</p> : (
                    <ul className="mt-2 grid gap-2">
                      {assistance.citations.map((citation) => (
                        <li key={citation.evidence_reference} className="border border-line p-3 text-sm">
                          Documento {citation.document_id} · página {citation.page_number ?? "N/A"} · chunk {citation.chunk_id ?? "N/A"}<br />
                          Método: {citation.retrieval_method} · qualidade: {citation.source_quality}<br />
                          <span className="text-steel">{citation.evidence_reference}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
              <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold">
                {assistance.executable_output ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
                <span>NON_PRODUCTION</span><span>SIMULATION_ONLY</span><span>executable_output=false</span><span>{assistance.review_status}</span>
              </div>
            </article>
          )}

          {!assistance && <p className="flex items-center gap-2 text-sm text-steel"><CircleDashed size={16} /> Assistência ainda não solicitada.</p>}
        </div>
      )}
    </section>
  );
}
