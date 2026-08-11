"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Download, ShieldAlert } from "lucide-react";

import { api, apiDownload } from "../lib/api";
import type {
  CatalogItem,
  ControlledEnvironmentResult,
  DigitalThreadManifest
} from "../lib/engineering-contracts";

type DocumentReference = { id: string; filename: string; status: string };
type Organization = { id: string; name: string; status: string };
type Props = { documents: DocumentReference[]; onError: (message: string) => void };

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
  const [busy, setBusy] = useState<"run" | "download" | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    api<Organization[]>("/organizations", { signal: controller.signal })
      .then(setOrganizations)
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
      .then(setCatalogs)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          onError(reason instanceof Error ? reason.message : "Falha ao carregar catálogos.");
        }
      });
    return () => controller.abort();
  }, [onError, organizationId]);

  async function run(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("run");
    setResult(null);
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
          fixture,
          datum_wcs_input: datumWcs
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
        holdout_id: holdoutId,
        sealed_reference_hash: sealedReferenceHash,
        questions_asked: ["Are G0-G8 supported by deterministic replayable evidence?"]
      };
      setResult(await api<ControlledEnvironmentResult>("/engineering/controlled-environment/runs", {
        method: "POST",
        body: JSON.stringify(payload)
      }));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Falha na validação controlada.");
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
          <input required value={fixture} onChange={(event) => setFixture(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm md:col-span-2">Datum/WCS proposto para confirmação
          <input required value={datumWcs} onChange={(event) => setDatumWcs(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm">Identificador do holdout selado
          <input required maxLength={255} value={holdoutId} onChange={(event) => setHoldoutId(event.target.value)} className="rounded border border-line bg-white p-2" />
        </label>
        <label className="grid gap-1 text-sm md:col-span-2">SHA-256 da referência selada
          <input required pattern="[0-9a-f]{64}" value={sealedReferenceHash} onChange={(event) => setSealedReferenceHash(event.target.value.toLowerCase())} className="rounded border border-line bg-white p-2 font-mono" />
        </label>
        <button disabled={busy !== null} className="self-end rounded bg-ink px-4 py-2 text-sm text-white disabled:opacity-50">
          {busy === "run" ? "Validando…" : "Executar validação controlada"}
        </button>
      </form>
      {result && <ControlledResult result={result} busy={busy !== null} onDownload={download} />}
    </section>
  );
}

function ControlledResult({ result, busy, onDownload }: {
  result: ControlledEnvironmentResult;
  busy: boolean;
  onDownload: () => void;
}) {
  return <div className="mt-5 grid gap-4" aria-live="polite">
    <div className="flex flex-wrap gap-2 text-xs font-semibold">
      <span className="border border-amber-400 px-2 py-1">{result.classification}</span>
      <span className="border border-amber-400 px-2 py-1">{result.review_state}</span>
      <span className="border border-red-400 px-2 py-1">G9: {result.g9_state}</span>
      <span className="border border-red-400 px-2 py-1">PHYSICAL_USE_AUTHORIZED=false</span>
    </div>
    <ol className="grid gap-2 md:grid-cols-2 lg:grid-cols-5">
      {result.blind_validation.gates.map((gate) => <li key={gate.gate} className="border border-line bg-white p-2 text-sm"><strong>{gate.gate}</strong> · {gate.status}</li>)}
    </ol>
    <ThreadSummary thread={result.digital_thread} />
    <pre className="max-h-72 overflow-auto border border-line bg-slate-950 p-3 text-xs text-green-200">{result.gcode_candidate.program}</pre>
    <button type="button" disabled={busy} onClick={onDownload} className="flex w-fit items-center gap-2 rounded bg-amber-900 px-4 py-2 text-sm text-white disabled:opacity-50">
      <Download size={16} /> Download controlado (.candidate.nc)
    </button>
    <p className="text-sm font-semibold text-red-800">Download não autoriza fabricação, machine-send, DNC, NC transfer, cycle start ou controle direto.</p>
  </div>;
}

function ThreadSummary({ thread }: { thread: DigitalThreadManifest }) {
  return <div className="border border-line bg-white p-3 text-sm">
    <p className="font-semibold">Digital Thread · {thread.status}</p>
    <p className="break-all text-xs text-steel">{thread.thread_id} · replay {thread.replay_hash}</p>
    <p className="mt-1">{thread.artifacts.length} artefatos imutáveis · G9 {thread.g9_state}</p>
  </div>;
}
