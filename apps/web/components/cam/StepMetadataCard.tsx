import type { StepGeometryInspection } from "../../lib/step-geometry-adapter";

export type CadDispatchUiState = Readonly<{
  phase: "IDLE" | "DISPATCHING" | "QUEUED" | "PROCESSING" | "COMPLETED" | "FAILED";
  jobId?: string;
  error?: string;
  warnings?: readonly string[];
}>;

export type CadDispatchUiAction =
  | Readonly<{ type: "START" }>
  | Readonly<{ type: "JOB"; jobId: string; status: "QUEUED" | "PROCESSING" | "COMPLETED" | "FAILED"; error?: string; warnings?: readonly string[] }>
  | Readonly<{ type: "RESET" }>;

export const idleDispatchState: CadDispatchUiState = { phase: "IDLE" };

export function reduceCadDispatchState(
  _state: CadDispatchUiState,
  action: CadDispatchUiAction,
): CadDispatchUiState {
  if (action.type === "RESET") return idleDispatchState;
  if (action.type === "START") return { phase: "DISPATCHING" };
  return {
    phase: action.status,
    jobId: action.jobId,
    ...(action.error ? { error: action.error } : {}),
    ...(action.warnings?.length ? { warnings: action.warnings } : {}),
  };
}

type Props = Readonly<{
  inspection: StepGeometryInspection;
  dispatchState?: CadDispatchUiState;
  onProcess?: () => void;
  onCancel?: () => void;
}>;

/** Client inspection and vector-analysis dispatch. It never enables physical emission. */
export function StepMetadataCard({
  inspection,
  dispatchState = idleDispatchState,
  onProcess,
  onCancel,
}: Props) {
  const { metadata } = inspection;
  const active = dispatchState.phase === "DISPATCHING" || dispatchState.phase === "QUEUED" || dispatchState.phase === "PROCESSING";
  return <details className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm">
    <summary className="cursor-pointer font-medium">Metadados da inspeção STEP local</summary>
    <dl className="mt-2 grid gap-1 text-slate-200">
      <div><dt className="inline text-slate-400">Schema: </dt><dd className="inline">{metadata.schema}</dd></div>
      <div><dt className="inline text-slate-400">Unidade: </dt><dd className="inline">{metadata.lengthUnit}</dd></div>
      <div><dt className="inline text-slate-400">Bytes lidos: </dt><dd className="inline">{metadata.bytesRead}</dd></div>
      <div><dt className="inline text-slate-400">B-Rep sólida: </dt><dd className="inline">{inspection.supported ? "Identificada textualmente" : "Não identificada"}</dd></div>
    </dl>
    {!inspection.supported && <p className="mt-2 text-amber-200">{inspection.reason}</p>}
    <p role="status" className="mt-2 text-xs text-slate-400">Inspeção estática local concluída. Resolução de perfil 2D analítico profundo requer despacho assíncrono.</p>
    <div className="mt-3 space-y-2 border-t border-slate-700 pt-3">
      <p className="text-xs text-cyan-100">Processamento restrito à análise vetorial e visualização 2D.</p>
      {dispatchState.phase === "IDLE" && <button type="button" disabled={!inspection.supported}
        onClick={onProcess} className="rounded bg-cyan-700 px-3 py-2 font-medium disabled:cursor-not-allowed disabled:bg-slate-700">
        Processar Geometria Analítica
      </button>}
      {(dispatchState.phase === "DISPATCHING" || dispatchState.phase === "QUEUED") &&
        <p role="status" aria-live="polite" aria-busy="true" className="text-cyan-200">
          <span aria-hidden="true" className="mr-2 inline-block animate-spin">◌</span>
          {dispatchState.phase === "DISPATCHING" ? "Enviando análise…" : "Análise incluída na fila…"}
        </p>}
      {dispatchState.phase === "PROCESSING" && <div role="status" aria-live="polite" className="space-y-1 text-cyan-200">
        <p>Análise geométrica em andamento…</p>
        <progress aria-label="Progresso indeterminado da análise geométrica" className="w-full" />
      </div>}
      {dispatchState.phase === "COMPLETED" && <p role="status" className="text-emerald-300">Perfil processado e pronto para renderização 2D.</p>}
      {dispatchState.phase === "COMPLETED" && dispatchState.warnings?.length ? <div role="alert" className="rounded border border-amber-500 bg-amber-950/40 p-2 text-amber-100">
        <p className="font-medium">Avisos de qualidade geométrica — revisão obrigatória:</p>
        <ul className="list-disc pl-5">{dispatchState.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul>
      </div> : null}
      {dispatchState.phase === "FAILED" && <p role="alert" className="text-rose-300">{dispatchState.error ?? "A análise geométrica falhou."}</p>}
      {active && <button type="button" onClick={onCancel} className="rounded border border-slate-400 px-3 py-2 text-slate-100">
        Cancelar análise
      </button>}
    </div>
  </details>;
}
