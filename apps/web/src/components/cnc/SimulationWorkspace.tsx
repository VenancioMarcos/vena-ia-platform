"use client";

import { useEffect, useState } from "react";
import {
  ToolpathCanvasViewer,
  type ToolpathSimulationPayload,
  type ToolpathSegment2D,
} from "./ToolpathCanvasViewer";

export interface SimulationTelemetry {
  xDiameterMm: number;
  zMm: number;
  feed: number | null;
  activeTool: string | null;
  isoBlock: string;
}

interface SimulationWorkspaceProps {
  payload?: ToolpathSimulationPayload;
  isoBlocks?: readonly string[];
  error?: string;
}

const EMPTY_BLOCK = "N/A — BLOCO ISO INDISPONÍVEL";

export function telemetryAtStep(
  payload: ToolpathSimulationPayload,
  isoBlocks: readonly string[],
  visibleSegmentCount: number,
): SimulationTelemetry {
  const count = Math.min(payload.segments.length, Math.max(0, visibleSegmentCount));
  const segment: ToolpathSegment2D = payload.segments[Math.max(0, count - 1)];
  const initial = count === 0;
  return {
    xDiameterMm: initial ? segment.x_start_mm : segment.x_end_mm,
    zMm: initial ? segment.z_start_mm : segment.z_end_mm,
    feed: initial ? null : segment.feed,
    activeTool: segment.active_tool,
    isoBlock: isoBlocks[count] ?? EMPTY_BLOCK,
  };
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-slate-700 bg-slate-950 p-3">
    <dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt>
    <dd className="mt-1 font-mono text-sm text-cyan-200">{value}</dd>
  </div>;
}

export function SimulationWorkspace({ payload, isoBlocks = [], error }: SimulationWorkspaceProps) {
  const [visibleSegments, setVisibleSegments] = useState(payload?.segments.length ?? 0);

  useEffect(() => {
    setVisibleSegments(payload?.segments.length ?? 0);
  }, [payload]);

  if (error || !payload || payload.segments.length === 0) {
    return <section className="space-y-4" aria-label="Painel de simulação indisponível">
      <div className="rounded-lg border border-red-500/60 bg-red-950/40 p-4 text-red-100" role="alert">
        Simulação indisponível: {error ?? "payload ausente ou sem segmentos verificáveis"}.
      </div>
      <div className="rounded-lg border border-amber-500/60 bg-amber-950/40 p-4 font-semibold text-amber-100">
        ESTADO: AUDITORIA NÃO-EXECUTÁVEL
      </div>
    </section>;
  }

  const telemetry = telemetryAtStep(payload, isoBlocks, visibleSegments);

  return <section className="space-y-6" aria-label="Workspace integrado de simulação CNC">
    <div className="rounded-lg border border-amber-500/60 bg-amber-950/40 p-4 text-amber-100">
      <p className="font-semibold">ESTADO: AUDITORIA NÃO-EXECUTÁVEL</p>
      <p className="mt-1 text-sm">G9=PENDING_AUTHORITATIVE_REVIEW · envio à máquina e início de ciclo desabilitados.</p>
    </div>

    <div className="grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(20rem,1fr)]">
      <ToolpathCanvasViewer
        payload={payload}
        visibleSegmentCount={visibleSegments}
        onVisibleSegmentCountChange={setVisibleSegments}
      />

      <aside className="space-y-4 rounded-xl border border-slate-700 bg-slate-900 p-4" aria-label="Telemetria sincronizada">
        <h2 className="text-lg font-semibold">Telemetry HUD</h2>
        <dl className="grid grid-cols-2 gap-3">
          <Metric label="X diâmetro" value={`${telemetry.xDiameterMm.toFixed(3)} mm`} />
          <Metric label="Z" value={`${telemetry.zMm.toFixed(3)} mm`} />
          <Metric label="Feed F" value={telemetry.feed === null ? "—" : telemetry.feed.toFixed(3)} />
          <Metric label="Ferramenta" value={telemetry.activeTool ?? "—"} />
        </dl>
        <div className="rounded-lg border border-cyan-800 bg-slate-950 p-3">
          <p className="text-xs uppercase tracking-wide text-slate-400">Bloco ISO ativo</p>
          <code className="mt-2 block break-words text-sm text-cyan-200">{telemetry.isoBlock}</code>
        </div>
      </aside>
    </div>

    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4" aria-label="Programa G-code somente leitura">
      <h2 className="mb-3 text-lg font-semibold">Programa ISO — somente leitura</h2>
      <pre className="max-h-80 overflow-auto rounded-lg bg-slate-950 p-4 font-mono text-sm leading-7 text-slate-200">
        {isoBlocks.map((block, index) => <code
          key={`${index}-${block}`}
          className={`block px-2 ${index === visibleSegments ? "bg-cyan-950 text-cyan-100" : ""}`}
          data-active-iso-block={index === visibleSegments ? "true" : undefined}
        >{block}</code>)}
      </pre>
    </section>
  </section>;
}
