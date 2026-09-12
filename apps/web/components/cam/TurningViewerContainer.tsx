"use client";

import { useState } from "react";
import type { SyntheticTurningExecutionResult } from "../../lib/turning-contracts";
import { cylinderSuccess } from "../../tests/fixtures/cylinder-success";
import { quantizedViolation } from "../../tests/fixtures/quantized-violation";
import { reconstructionFailure } from "../../tests/fixtures/reconstruction-failure";
import { TurningProfile2D } from "./TurningProfile2D";
import { StepUploadZone } from "./StepUploadZone";
import { inspectStepGeometry, type StepGeometryInspection } from "../../lib/step-geometry-adapter";

const samples = {
  CYLINDER_SUCCESS: { label: "Cilindro — sucesso sintético", result: cylinderSuccess },
  QUANTIZED_VIOLATION: { label: "Violação após quantização", result: quantizedViolation },
  RECONSTRUCTION_FAILURE: { label: "Falha de reconstrução", result: reconstructionFailure },
} as const;
export type TurningFixtureSelection = keyof typeof samples;
export type LocalStepFileMetadata = Readonly<{ filename: string; sizeBytes: number }>;

function formatFileSize(sizeBytes: number): string {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Local fixture preview only; initialSelection is read once on mount. */
export function TurningViewerContainer({
  initialSelection = "CYLINDER_SUCCESS",
  initialLocalStepFile = null,
}: Readonly<{
  initialSelection?: TurningFixtureSelection;
  initialLocalStepFile?: LocalStepFileMetadata | null;
}>) {
  const [selection, setSelection] = useState<TurningFixtureSelection>(initialSelection);
  const [localStepFile, setLocalStepFile] = useState<LocalStepFileMetadata | null>(initialLocalStepFile);
  const [geometryInspection, setGeometryInspection] = useState<StepGeometryInspection | null>(null);
  const result: SyntheticTurningExecutionResult = samples[selection].result;
  // Never substitute the nominal plan when reconstruction did not produce a plan.
  const plan = result.quantized_plan;
  const moves = plan?.operations.flatMap(operation => operation.moves) ?? [];
  const passes = plan?.operations.reduce((total, operation) => total + operation.passes_count, 0);
  const feeds = [...new Set(moves.map(move => move.feed_rate_type))];
  return <section aria-label="Inspeção de fixtures de torneamento" className="space-y-4 rounded-xl border border-slate-700 bg-slate-950 p-4 text-slate-100">
    <h2 className="text-lg font-semibold">Torneamento · inspeção sintética</h2>
    <p className="text-sm text-slate-300">Exemplos locais de teste. Visualização sem autorização para uso físico.</p>
    <StepUploadZone
      onAccepted={file => {
        setLocalStepFile({ filename: file.name, sizeBytes: file.size });
        void inspectStepGeometry(file).then(setGeometryInspection, () => setGeometryInspection(null));
      }}
      onCleared={() => { setLocalStepFile(null); setGeometryInspection(null); }}
    />
    {localStepFile && <div role="status" aria-live="polite" className="rounded-lg border border-amber-400 bg-amber-950/30 p-3 text-sm text-amber-100">
      <p className="font-medium">Arquivo local carregado — Pipeline de geometria analítica aguardando despacho.</p>
      <p>{localStepFile.filename} · {formatFileSize(localStepFile.sizeBytes)}</p>
      <p className="mt-1 text-xs">Emissão de G-code e despacho físico permanecem bloqueados.</p>
    </div>}
    {geometryInspection && <details className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm">
      <summary className="cursor-pointer font-medium">Metadados da inspeção STEP local</summary>
      <dl className="mt-2 grid gap-1 text-slate-200">
        <div><dt className="inline text-slate-400">Schema: </dt><dd className="inline">{geometryInspection.metadata.schema}</dd></div>
        <div><dt className="inline text-slate-400">Unidade: </dt><dd className="inline">{geometryInspection.metadata.lengthUnit}</dd></div>
        <div><dt className="inline text-slate-400">Bytes lidos: </dt><dd className="inline">{geometryInspection.metadata.bytesRead}</dd></div>
      </dl>
      {!geometryInspection.supported && <p className="mt-2 text-amber-200">{geometryInspection.reason}</p>}
      <p className="mt-2 text-xs text-slate-400">A análise geométrica definitiva depende de despacho assíncrono autorizado.</p>
    </details>}
    <label className="block text-sm">Cenário de teste
      <select value={selection} onChange={event => {
        const next = event.target.value;
        if (next === "CYLINDER_SUCCESS" || next === "QUANTIZED_VIOLATION" || next === "RECONSTRUCTION_FAILURE") setSelection(next);
      }} className="ml-3 rounded border border-slate-600 bg-slate-900 px-3 py-2">
        {Object.entries(samples).map(([key, sample]) => <option key={key} value={key}>{sample.label}</option>)}
      </select>
    </label>
    <div className="flex flex-wrap gap-2 text-xs">
      <span className="rounded bg-slate-800 px-2 py-1">NON_PRODUCTION</span>
      <span className="rounded bg-slate-800 px-2 py-1">PHYSICAL_USE_AUTHORIZED: FALSE</span>
      <span className="rounded bg-slate-800 px-2 py-1">G9: PENDENTE</span>
    </div>
    <div aria-live="polite" className="min-w-0 break-words">
      <dl className="grid gap-2 text-sm">
        <div><dt className="inline text-slate-400">Status: </dt><dd className="inline">{result.pipeline_status}</dd></div>
        <div><dt className="inline text-slate-400">Plano exibido: </dt><dd className="inline">Quantizado</dd></div>
        <div><dt className="inline text-slate-400">Passadas: </dt><dd className="inline">{passes ?? "Não disponível"}</dd></div>
        <div><dt className="inline text-slate-400">Movimentos: </dt><dd className="inline">{plan ? moves.length : "Não disponível"}</dd></div>
        <div><dt className="inline text-slate-400">Unidade de avanço: </dt><dd className="inline">{feeds.join(", ") || "Não disponível"}</dd></div>
      </dl>
      {result.failure_reason && <p className="mt-2 text-sm">Motivo: {result.failure_reason}</p>}
      {plan ? <TurningProfile2D plan={plan} width={640} height={400} className="mt-4 h-auto max-w-full rounded" /> :
        <p className="mt-4 rounded bg-slate-800 p-4" role="status">Plano quantizado indisponível: a reconstrução não produziu uma trajetória para exibir.</p>}
    </div>
    <p className="text-xs text-slate-300">Movimentos: rápido em âmbar · corte em ciano · recuo em magenta. Cores não indicam aprovação física.</p>
  </section>;
}
