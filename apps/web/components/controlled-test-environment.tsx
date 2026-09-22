"use client";

import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Download, ShieldAlert } from "lucide-react";

import { api, apiDownload } from "../lib/api";
import { MachiningTechnicalReportViewer } from "../src/components/cnc/MachiningTechnicalReportViewer";
import type {
  CatalogItem,
  ControlledEnvironmentResult,
  DigitalThreadManifest
} from "../lib/engineering-contracts";

type DocumentReference = { id: string; filename: string; status: string };
type Organization = { id: string; name: string; status: string };
type Props = { documents: DocumentReference[]; onError: (message: string) => void };
type HumanReview = {
  id: string;
  review_state: "REQUIRES_HUMAN_REVIEW" | "APPROVED_FOR_CONTROLLED_DOWNLOAD";
  review_note: string | null;
};
type Feedback = { id: string; rating: number; comment: string | null };
const CONTROLLED_RUN_TIMEOUT_MS = 120_000;

function point(value: string): number[] {
  const values = value.split(",").map((item) => Number(item.trim()));
  if (values.length !== 3 || values.some((item) => !Number.isFinite(item))) {
    throw new Error("Informe exatamente três coordenadas XYZ finitas, separadas por vírgula.");
  }
  return values;
}

export function ControlledTestEnvironment({ documents, onError }: Props) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [catalogs, setCatalogs] = useState<CatalogItem[]>([]);
  const [organizationId, setOrganizationId] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [materialId, setMaterialId] = useState("");
  const [machineId, setMachineId] = useState("");
  const [toolId, setToolId] = useState("");
  const [stockMinimum, setStockMinimum] = useState("-1,-1,-1");
  const [stockMaximum, setStockMaximum] = useState("101,101,101");
  const [machineMinimum, setMachineMinimum] = useState("-100,-100,-100");
  const [machineMaximum, setMachineMaximum] = useState("200,200,200");
  const [toolDiameter, setToolDiameter] = useState("0.5");
  const [fluteLength, setFluteLength] = useState("10");
  const [clearanceZ, setClearanceZ] = useState("150");
  const [retractZ, setRetractZ] = useState("140");
  const [feed, setFeed] = useState("800");
  const [fixture, setFixture] = useState("");
  const [datumWcs, setDatumWcs] = useState("");
  const [holdoutId, setHoldoutId] = useState("");
  const [sealedReferenceHash, setSealedReferenceHash] = useState("");
  const [result, setResult] = useState<ControlledEnvironmentResult | null>(null);
  const [downloadAcknowledged, setDownloadAcknowledged] = useState(false);
  const [review, setReview] = useState<HumanReview | null>(null);
  const [reviewNote, setReviewNote] = useState(
    "Revisei o resultado técnico e compreendo que o arquivo é um candidato não produtivo."
  );
  const [rating, setRating] = useState("5");
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [busy, setBusy] = useState<"run" | "review" | "download" | "feedback" | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    api<Organization[]>("/organizations", { signal: controller.signal })
      .then((items) => {
        setOrganizations(items);
        setOrganizationId((current) => current || items[0]?.id || "");
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          onError(reason instanceof Error ? reason.message : "Falha ao carregar organizações.");
        }
      });
    return () => controller.abort();
  }, [onError]);

  useEffect(() => {
    if (!organizationId) {
      setCatalogs([]);
      return;
    }
    const controller = new AbortController();
    api<CatalogItem[]>(`/engineering/catalogs?organization_id=${organizationId}`, {
      signal: controller.signal
    })
      .then((items) => {
        setCatalogs(items);
        setMaterialId((current) => current || items.find((item) => item.kind === "MATERIAL")?.id || "");
        setMachineId((current) => current || items.find((item) => item.kind === "MACHINE")?.id || "");
        setToolId((current) => current || items.find((item) => item.kind === "TOOL")?.id || "");
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          onError(reason instanceof Error ? reason.message : "Falha ao carregar catálogos.");
        }
      });
    return () => controller.abort();
  }, [onError, organizationId]);

  useEffect(() => {
    const stepDocument = documents.find((item) => /\.(step|stp)$/i.test(item.filename));
    if (stepDocument) setDocumentId((current) => current || stepDocument.id);
  }, [documents]);

  async function sha256Hex(value: string): Promise<string> {
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
    return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
  }

  async function run(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("run");
    setResult(null);
    setReview(null);
    setFeedback(null);
    setDownloadAcknowledged(false);
    try {
      const payload = {
        organization_id: organizationId,
        planning: {
          document_id: documentId,
          stock: {
            status: "PROVIDED",
            minimum: point(stockMinimum),
            maximum: point(stockMaximum),
            unit: "mm",
            source_ref: "authorized-user-input:controlled-test-environment"
          },
          manufacturing_intent: "milling",
          material_id: materialId,
          machine_id: machineId,
          tool_id: toolId,
          fixture: fixture || "Beta 1 fixture requires human confirmation",
          datum_wcs_input: datumWcs || "Candidate G54 requires human confirmation"
        },
        tool: {
          tool_id: toolId,
          diameter_mm: Number(toolDiameter),
          flute_length_mm: Number(fluteLength)
        },
        machine_minimum: point(machineMinimum),
        machine_maximum: point(machineMaximum),
        clearance_z_mm: Number(clearanceZ),
        retract_z_mm: Number(retractZ),
        feed_mm_min: Number(feed),
        fixture_keep_outs: [],
        holdout_id: holdoutId || `beta1-${documentId}`,
        sealed_reference_hash: sealedReferenceHash || await sha256Hex(`vena-ia-beta1:${documentId}`),
        questions_asked: ["Are G0-G8 supported by deterministic replayable evidence?"]
      };
      setResult(await api<ControlledEnvironmentResult>("/engineering/controlled-environment/runs", {
        method: "POST",
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(CONTROLLED_RUN_TIMEOUT_MS)
      }));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha na validação controlada.");
    } finally {
      setBusy(null);
    }
  }

  async function persistReview() {
    if (!result || !downloadAcknowledged) return;
    setBusy("review");
    try {
      setReview(await api<HumanReview>(`/product-flow/results/${result.result_id}/review`, {
        method: "POST",
        body: JSON.stringify({ acknowledgement: true, note: reviewNote })
      }));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha ao registrar revisão humana.");
    } finally {
      setBusy(null);
    }
  }

  async function download() {
    if (!result) return;
    setBusy("download");
    try {
      const file = await apiDownload("/engineering/controlled-environment/download", {
        method: "POST",
        body: JSON.stringify({
          organization_id: organizationId,
          result_id: result.result_id,
          gcode_candidate: result.gcode_candidate,
          blind_validation: result.blind_validation,
          digital_thread: result.digital_thread,
          download_token: result.download_token
        })
      });
      const url = URL.createObjectURL(file.blob);
      const anchor = window.document.createElement("a");
      anchor.href = url;
      anchor.download = file.filename;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha no download controlado.");
    } finally {
      setBusy(null);
    }
  }

  async function submitFeedback(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!result) return;
    setBusy("feedback");
    try {
      setFeedback(await api<Feedback>(`/product-flow/results/${result.result_id}/feedback`, {
        method: "POST",
        body: JSON.stringify({
          rating: Number(rating),
          comment: feedbackComment.trim() || null
        })
      }));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha ao enviar avaliação.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <section aria-labelledby="controlled-environment-title" className="mt-8 border border-amber-300 bg-amber-50 p-5">
      <h2 id="controlled-environment-title" className="flex items-center gap-2 font-semibold">
        <ShieldAlert size={18} /> Ambiente de teste controlado CAD → G-code candidato
      </h2>
      <p className="mt-1 text-sm text-steel">
        NON_PRODUCTION · REQUIRES_HUMAN_REVIEW · G9 permanece server-side e pendente.
      </p>
      <form onSubmit={run} className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        <label className="grid gap-1 text-sm">Organização
          <select required value={organizationId} onChange={(event) => setOrganizationId(event.target.value)} className="rounded border border-line bg-white p-2">
            <option value="">Selecione</option>
            {organizations.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
        </label>
        <label className="grid gap-1 text-sm">Documento CAD controlado
          <select required value={documentId} onChange={(event) => setDocumentId(event.target.value)} className="rounded border border-line bg-white p-2">
            <option value="">Selecione</option>
            {documents.map((item) => <option key={item.id} value={item.id}>{item.filename}</option>)}
          </select>
        </label>
        {(["MATERIAL", "MACHINE", "TOOL"] as const).map((kind) => {
          const value = kind === "MATERIAL" ? materialId : kind === "MACHINE" ? machineId : toolId;
          const setter = kind === "MATERIAL" ? setMaterialId : kind === "MACHINE" ? setMachineId : setToolId;
          return <label key={kind} className="grid gap-1 text-sm">{kind}
            <select required value={value} onChange={(event) => setter(event.target.value)} className="rounded border border-line bg-white p-2">
              <option value="">Selecione</option>
              {catalogs.filter((item) => item.kind === kind).map((item) => <option key={item.id} value={item.id}>{item.code} · {item.name}</option>)}
            </select>
          </label>;
        })}
        <label className="grid gap-1 text-sm">Stock mínimo XYZ (mm)
          <input required value={stockMinimum} onChange={(event) => setStockMinimum(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Stock máximo XYZ (mm)
          <input required value={stockMaximum} onChange={(event) => setStockMaximum(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Máquina mínimo XYZ (mm)
          <input required value={machineMinimum} onChange={(event) => setMachineMinimum(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Máquina máximo XYZ (mm)
          <input required value={machineMaximum} onChange={(event) => setMachineMaximum(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Diâmetro da ferramenta (mm)
          <input required type="number" min="0.001" step="any" value={toolDiameter} onChange={(event) => setToolDiameter(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Comprimento útil (mm)
          <input required type="number" min="0.001" step="any" value={fluteLength} onChange={(event) => setFluteLength(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Clearance Z (mm)
          <input required type="number" step="any" value={clearanceZ} onChange={(event) => setClearanceZ(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Retract Z (mm)
          <input required type="number" step="any" value={retractZ} onChange={(event) => setRetractZ(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Feed (mm/min)
          <input required type="number" min="0.001" step="any" value={feed} onChange={(event) => setFeed(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm md:col-span-2">Fixture / restrições revisáveis
          <input placeholder="Opcional: será criado um valor seguro para revisão" value={fixture} onChange={(event) => setFixture(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm md:col-span-2">Datum/WCS proposto para confirmação
          <input placeholder="Opcional: G54 candidato será marcado para revisão" value={datumWcs} onChange={(event) => setDatumWcs(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Identificador do holdout selado
          <input maxLength={255} placeholder="Gerado automaticamente" value={holdoutId} onChange={(event) => setHoldoutId(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm md:col-span-2">SHA-256 da referência selada
          <input pattern="[0-9a-f]{64}" placeholder="Gerado automaticamente a partir do documento" value={sealedReferenceHash} onChange={(event) => setSealedReferenceHash(event.target.value.toLowerCase())} className="rounded border border-line bg-white p-2 font-mono" />
        </label>
        <button disabled={busy !== null} className="self-end rounded bg-ink px-4 py-2 text-sm text-white disabled:opacity-50">
          {busy === "run" ? "Validando…" : "Executar validação controlada"}
        </button>
      </form>
      {result && <ControlledResult
        result={result}
        busy={busy !== null}
        downloadAcknowledged={downloadAcknowledged}
        onDownloadAcknowledged={setDownloadAcknowledged}
        review={review}
        reviewNote={reviewNote}
        onReviewNote={setReviewNote}
        onPersistReview={persistReview}
        onDownload={download}
        feedback={feedback}
        rating={rating}
        onRating={setRating}
        feedbackComment={feedbackComment}
        onFeedbackComment={setFeedbackComment}
        onSubmitFeedback={submitFeedback}
      />}
    </section>
  );
}

function ControlledResult({
  result,
  busy,
  downloadAcknowledged,
  onDownloadAcknowledged,
  review,
  reviewNote,
  onReviewNote,
  onPersistReview,
  onDownload,
  feedback,
  rating,
  onRating,
  feedbackComment,
  onFeedbackComment,
  onSubmitFeedback
}: {
  result: ControlledEnvironmentResult;
  busy: boolean;
  downloadAcknowledged: boolean;
  onDownloadAcknowledged: (acknowledged: boolean) => void;
  review: HumanReview | null;
  reviewNote: string;
  onReviewNote: (note: string) => void;
  onPersistReview: () => void;
  onDownload: () => void;
  feedback: Feedback | null;
  rating: string;
  onRating: (rating: string) => void;
  feedbackComment: string;
  onFeedbackComment: (comment: string) => void;
  onSubmitFeedback: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return <div className="mt-5 grid gap-4" aria-live="polite">
    <div className="flex flex-wrap gap-2 text-xs font-semibold">
      <span className="border border-amber-400 px-2 py-1">{result.classification}</span>
      <span className="border border-amber-400 px-2 py-1">{result.review_state}</span>
      <span className="border border-red-400 px-2 py-1">G9: {result.g9_state}</span>
      <span className="border border-red-400 px-2 py-1">PHYSICAL_USE_AUTHORIZED=false</span>
    </div>
    <MachiningTechnicalReportViewer controlledResult={result} />
    <ol className="grid gap-2 md:grid-cols-2 lg:grid-cols-5">
      {result.blind_validation.gates.map((gate) => <li key={gate.gate} className="border border-line bg-white p-2 text-sm"><strong>{gate.gate}</strong> · {gate.status}</li>)}
    </ol>
    <div className="grid gap-3 lg:grid-cols-3">
      <EvidenceCard title="Manufacturing Geometry">
        <p>{result.manufacturing_model.status} · topologia {result.manufacturing_model.final_geometry.topology_valid ? "válida" : "não validada"}</p>
        <p>Stock: {result.manufacturing_model.stock.status} · contém geometria: {String(result.manufacturing_model.stock.contains_final_geometry)}</p>
        <p>{result.manufacturing_model.removal_regions.length} regiões removíveis · {result.manufacturing_model.final_geometry.normalized_unit}</p>
        <p className="break-all text-xs text-steel">geometry {result.manufacturing_model.final_geometry.source_geometry_hash}</p>
      </EvidenceCard>
      <EvidenceCard title="Verified Process Plan">
        <p>{result.manufacturing_model.verification.status} · coherent={String(result.manufacturing_model.verification.coherent)}</p>
        <p>{result.manufacturing_model.operation_candidates.length} operações candidatas</p>
        {result.manufacturing_model.operation_candidates.map((operation) =>
          <p key={operation.candidate_id}>{operation.operation_class} · {operation.status} · executable_output=false</p>
        )}
        <p className="break-all text-xs text-steel">replay {result.manufacturing_model.verification.deterministic_replay_hash}</p>
      </EvidenceCard>
      <EvidenceCard title="Toolpath candidato">
        <p>{result.toolpath.status} · {result.toolpath.segments.length} segmentos lineares</p>
        <p>{result.toolpath.target_region_ids.length} regiões alvo · production_authority=false</p>
        <p>Verificação: {result.toolpath.verification.status}</p>
        <p className="break-all text-xs text-steel">replay {result.toolpath.verification.deterministic_replay_hash}</p>
      </EvidenceCard>
    </div>
    <EvidenceCard title="Level-2 bounded evidence">
      <p>{result.level2_evidence.status} · {result.level2_evidence.reconstructed_segment_count} segmentos reconstruídos</p>
      <p>coverage={result.level2_evidence.target_coverage} · remaining={result.level2_evidence.remaining_material}</p>
      <p>gouge={String(result.level2_evidence.gouge_detected)} · protected-surface={String(result.level2_evidence.protected_surface_violation)} · physical_validation=false</p>
      <p className="break-all text-xs text-steel">replay {result.level2_evidence.replay_hash}</p>
    </EvidenceCard>
    <ThreadSummary thread={result.digital_thread} />
    <div className="border border-line bg-white p-3 text-sm">
      <p className="font-semibold">G9 Review Package · {result.g9_review_package.g9_state}</p>
      <p className="break-all text-xs text-steel">
        {result.g9_review_package.package_id} · hash {result.g9_review_package.package_hash}
      </p>
      <p className="mt-1">
        {Object.keys(result.g9_review_package.artifact_hashes).length} artefatos vinculados ·
        autoridade automática=false
      </p>
    </div>
    <pre className="max-h-72 overflow-auto border border-line bg-slate-950 p-3 text-xs text-green-200">{result.gcode_candidate.program}</pre>
    <label className="flex items-start gap-2 border border-red-300 bg-red-50 p-3 text-sm font-semibold text-red-900">
      <input type="checkbox" checked={downloadAcknowledged} onChange={(event) => onDownloadAcknowledged(event.target.checked)} />
      Confirmo que este arquivo é NON_PRODUCTION, requer revisão humana e não está autorizado para uso físico.
    </label>
    <label className="grid gap-1 text-sm font-semibold">
      Nota da revisão humana
      <textarea minLength={10} maxLength={2000} value={reviewNote} onChange={(event) => onReviewNote(event.target.value)} className="min-h-24 rounded border border-line bg-white p-2 font-normal" />
    </label>
    <button type="button" disabled={busy || !downloadAcknowledged || reviewNote.trim().length < 10 || review?.review_state === "APPROVED_FOR_CONTROLLED_DOWNLOAD"} onClick={onPersistReview} className="w-fit rounded bg-ink px-4 py-2 text-sm text-white disabled:opacity-50">
      {review?.review_state === "APPROVED_FOR_CONTROLLED_DOWNLOAD" ? "Revisão registrada" : "Registrar revisão humana"}
    </button>
    {review?.review_state === "APPROVED_FOR_CONTROLLED_DOWNLOAD" && (
      <p className="border border-green-300 bg-green-50 p-3 text-sm font-semibold text-green-900">
        Revisão persistida: {review.review_state}
      </p>
    )}
    <button type="button" disabled={busy || review?.review_state !== "APPROVED_FOR_CONTROLLED_DOWNLOAD"} onClick={onDownload} className="flex w-fit items-center gap-2 rounded bg-amber-900 px-4 py-2 text-sm text-white disabled:opacity-50">
      <Download size={16} /> Download controlado (.candidate.nc)
    </button>
    <p className="text-sm font-semibold text-red-800">Download não autoriza fabricação, machine-send, DNC, NC transfer, cycle start ou controle direto.</p>
    {review?.review_state === "APPROVED_FOR_CONTROLLED_DOWNLOAD" && (
      feedback ? (
        <p className="border border-green-300 bg-green-50 p-3 text-sm font-semibold text-green-900">
          Avaliação registrada: {feedback.rating}/5.
        </p>
      ) : (
        <form onSubmit={onSubmitFeedback} className="grid gap-3 border border-line bg-white p-4">
          <h3 className="font-semibold">Avalie o resultado</h3>
          <label className="grid gap-1 text-sm">Nota
            <select value={rating} onChange={(event) => onRating(event.target.value)} className="w-fit rounded border border-line p-2">
              {[5, 4, 3, 2, 1].map((value) => <option key={value} value={value}>{value}/5</option>)}
            </select>
          </label>
          <label className="grid gap-1 text-sm">Comentário opcional
            <textarea maxLength={2000} value={feedbackComment} onChange={(event) => onFeedbackComment(event.target.value)} className="min-h-24 rounded border border-line p-2" />
          </label>
          <button disabled={busy} className="w-fit rounded bg-machine px-4 py-2 text-sm text-white disabled:opacity-50">Enviar avaliação</button>
        </form>
      )
    )}
  </div>;
}

function ThreadSummary({ thread }: { thread: DigitalThreadManifest }) {
  return <div className="border border-line bg-white p-3 text-sm">
    <p className="font-semibold">Digital Thread · {thread.status}</p>
    <p className="break-all text-xs text-steel">{thread.thread_id} · replay {thread.replay_hash}</p>
    <p className="mt-1">{thread.artifacts.length} artefatos imutáveis · G9 {thread.g9_state}</p>
    <ol className="mt-2 grid gap-1 md:grid-cols-2">
      {thread.artifacts.map((artifact) =>
        <li key={artifact.artifact_id} className="break-all text-xs">
          {artifact.artifact_type} · {artifact.schema_version} · {artifact.lifecycle_status} · {artifact.content_hash}
        </li>
      )}
    </ol>
  </div>;
}

function EvidenceCard({ title, children }: { title: string; children: ReactNode }) {
  return <section aria-label={title} className="border border-line bg-white p-3 text-sm">
    <h3 className="font-semibold">{title}</h3>
    <div className="mt-1 grid gap-1">{children}</div>
  </section>;
}
