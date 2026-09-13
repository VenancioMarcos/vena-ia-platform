"use client";

import { useEffect, useRef, useState } from "react";

export type ToolpathMotionType = "RAPID" | "LINEAR";

export interface ToolpathSegment2D {
  motion_type: ToolpathMotionType;
  x_start_mm: number;
  z_start_mm: number;
  x_end_mm: number;
  z_end_mm: number;
  feed: number | null;
  active_tool: string | null;
}

export interface MachineEnvelope2D {
  x_min_mm: number;
  x_max_mm: number;
  z_min_mm: number;
  z_max_mm: number;
  chuck_exclusion_zone: {
    x_min_mm: number;
    x_max_mm: number;
    z_min_mm: number;
    z_max_mm: number;
  };
}

export interface TurningStock2D {
  diameter_mm: number;
  z_min_mm: number;
  z_max_mm: number;
}

export interface ToolpathSimulationPayload {
  status: "SIMULATION_READY_REQUIRES_REVIEW";
  source_plan_id: string | null;
  controller_profile: "FANUC_0I" | "SIEMENS_840D" | "HAAS" | "SIMULATED_STUB";
  segments: readonly ToolpathSegment2D[];
  machine_envelope: MachineEnvelope2D;
  stock: TurningStock2D;
  chuck_proximity: {
    minimum_clearance_mm: number;
    threshold_mm: number;
    closest_segment_index: number;
    warning_code: "WARNING_PROXIMITY_CHUCK" | null;
  };
  coordinate_convention: "LATHE_X_DIAMETER_Z";
  safety_flags: {
    physical_use_authorized: false;
    g9: "PENDING_AUTHORITATIVE_REVIEW";
    no_human_review_bypass: true;
    machine_send: false;
    dnc: false;
    nc_transfer: false;
    cycle_start: false;
    emission_status: "CONTROLLER_PROFILE_UNRESOLVED";
    executable_output: false;
  };
}

interface ToolpathCanvasViewerProps {
  payload: ToolpathSimulationPayload;
  width?: number;
  height?: number;
  className?: string;
  visibleSegmentCount?: number;
  onVisibleSegmentCountChange?: (count: number) => void;
}

const PADDING = 32;

function finite(value: number): boolean {
  return Number.isFinite(value);
}

function isRenderable(payload: ToolpathSimulationPayload, width: number, height: number): boolean {
  const envelope = payload.machine_envelope;
  return (
    payload.segments.length > 0 &&
    width > PADDING * 2 &&
    height > PADDING * 2 &&
    [
      envelope.x_min_mm,
      envelope.x_max_mm,
      envelope.z_min_mm,
      envelope.z_max_mm,
      payload.stock.diameter_mm,
      payload.stock.z_min_mm,
      payload.stock.z_max_mm,
    ].every(finite) &&
    envelope.x_min_mm < envelope.x_max_mm &&
    envelope.z_min_mm < envelope.z_max_mm
  );
}

function drawToolpath(
  context: CanvasRenderingContext2D,
  payload: ToolpathSimulationPayload,
  segmentCount: number,
  width: number,
  height: number,
): void {
  const envelope = payload.machine_envelope;
  const xScale = (height - PADDING * 2) / (envelope.x_max_mm - envelope.x_min_mm);
  const zScale = (width - PADDING * 2) / (envelope.z_max_mm - envelope.z_min_mm);
  const toCanvasX = (z: number) => PADDING + (z - envelope.z_min_mm) * zScale;
  const toCanvasY = (x: number) => height - PADDING - (x - envelope.x_min_mm) * xScale;

  context.clearRect(0, 0, width, height);
  context.fillStyle = "#07111f";
  context.fillRect(0, 0, width, height);

  context.strokeStyle = "#64748b";
  context.lineWidth = 1;
  context.setLineDash([4, 4]);
  if (envelope.x_min_mm <= 0 && envelope.x_max_mm >= 0) {
    context.beginPath();
    context.moveTo(PADDING, toCanvasY(0));
    context.lineTo(width - PADDING, toCanvasY(0));
    context.stroke();
  }
  if (envelope.z_min_mm <= 0 && envelope.z_max_mm >= 0) {
    context.beginPath();
    context.moveTo(toCanvasX(0), PADDING);
    context.lineTo(toCanvasX(0), height - PADDING);
    context.stroke();
  }

  const stockX = Math.min(payload.stock.diameter_mm, envelope.x_max_mm);
  context.fillStyle = "rgba(148, 163, 184, 0.14)";
  context.strokeStyle = "#94a3b8";
  context.setLineDash([]);
  context.fillRect(
    toCanvasX(payload.stock.z_min_mm),
    toCanvasY(stockX),
    toCanvasX(payload.stock.z_max_mm) - toCanvasX(payload.stock.z_min_mm),
    toCanvasY(Math.max(0, envelope.x_min_mm)) - toCanvasY(stockX),
  );
  context.strokeRect(
    toCanvasX(payload.stock.z_min_mm),
    toCanvasY(stockX),
    toCanvasX(payload.stock.z_max_mm) - toCanvasX(payload.stock.z_min_mm),
    toCanvasY(Math.max(0, envelope.x_min_mm)) - toCanvasY(stockX),
  );

  const chuck = envelope.chuck_exclusion_zone;
  const proximityWarning = payload.chuck_proximity.warning_code === "WARNING_PROXIMITY_CHUCK";
  context.fillStyle = proximityWarning ? "rgba(239, 68, 68, 0.48)" : "rgba(239, 68, 68, 0.28)";
  context.strokeStyle = proximityWarning ? "#fca5a5" : "#ef4444";
  context.lineWidth = proximityWarning ? 4 : 1;
  context.fillRect(
    toCanvasX(chuck.z_min_mm),
    toCanvasY(chuck.x_max_mm),
    toCanvasX(chuck.z_max_mm) - toCanvasX(chuck.z_min_mm),
    toCanvasY(chuck.x_min_mm) - toCanvasY(chuck.x_max_mm),
  );
  context.strokeRect(
    toCanvasX(chuck.z_min_mm),
    toCanvasY(chuck.x_max_mm),
    toCanvasX(chuck.z_max_mm) - toCanvasX(chuck.z_min_mm),
    toCanvasY(chuck.x_min_mm) - toCanvasY(chuck.x_max_mm),
  );

  payload.segments.slice(0, segmentCount).forEach((segment) => {
    context.beginPath();
    context.moveTo(toCanvasX(segment.z_start_mm), toCanvasY(segment.x_start_mm));
    context.lineTo(toCanvasX(segment.z_end_mm), toCanvasY(segment.x_end_mm));
    context.strokeStyle = segment.motion_type === "RAPID" ? "#f59e0b" : "#06b6d4";
    context.lineWidth = 2;
    context.setLineDash(segment.motion_type === "RAPID" ? [7, 5] : []);
    context.stroke();
  });
  context.setLineDash([]);
}

export function ToolpathCanvasViewer({
  payload,
  width = 760,
  height = 440,
  className = "",
  visibleSegmentCount,
  onVisibleSegmentCountChange,
}: ToolpathCanvasViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [internalVisibleSegments, setInternalVisibleSegments] = useState(payload.segments.length);
  const [playing, setPlaying] = useState(false);
  const renderable = isRenderable(payload, width, height);
  const visibleSegments = Math.min(
    payload.segments.length,
    Math.max(0, visibleSegmentCount ?? internalVisibleSegments),
  );
  const proximityWarning = payload.chuck_proximity.warning_code === "WARNING_PROXIMITY_CHUCK";

  const updateVisibleSegments = (count: number) => {
    const boundedCount = Math.min(payload.segments.length, Math.max(0, count));
    if (visibleSegmentCount === undefined) setInternalVisibleSegments(boundedCount);
    onVisibleSegmentCountChange?.(boundedCount);
  };

  useEffect(() => {
    setInternalVisibleSegments(payload.segments.length);
    setPlaying(false);
  }, [payload]);

  useEffect(() => {
    if (!playing || !renderable) return;
    const timer = window.setInterval(() => {
      if (visibleSegments >= payload.segments.length) {
        setPlaying(false);
        return;
      }
      updateVisibleSegments(visibleSegments + 1);
    }, 350);
    return () => window.clearInterval(timer);
  }, [payload.segments.length, playing, renderable, visibleSegments]);

  useEffect(() => {
    const context = canvasRef.current?.getContext("2d");
    if (!context || !renderable) return;
    drawToolpath(context, payload, visibleSegments, width, height);
  }, [height, payload, renderable, visibleSegments, width]);

  return (
    <section className={`rounded-xl border border-slate-700 bg-slate-950 p-4 text-slate-100 ${className}`.trim()}>
      <div className="mb-4 rounded-md border border-amber-500/70 bg-amber-950/50 px-3 py-2 text-sm font-semibold text-amber-200" role="status">
        AUDIT ONLY - PHYSICAL_USE_AUTHORIZED=FALSE
      </div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3 text-sm">
        <div>
          <p className="font-semibold">Simulação vetorial 2D — X diâmetro / Z</p>
          <p className="text-slate-400">{payload.controller_profile} · revisão humana obrigatória</p>
        </div>
        <div className="flex gap-4 text-xs" aria-label="Legenda da trajetória">
          <span className="text-amber-400">--- G00 rápido</span>
          <span className="text-cyan-400">━ G01 corte</span>
          <span className="text-red-400">■ Zona da placa</span>
        </div>
      </div>

      {renderable ? (
        <>
          <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`h-auto w-full rounded-md border border-slate-800 ${proximityWarning ? "animate-pulse ring-2 ring-red-500" : ""}`.trim()}
            aria-label="Trajetória de torneamento em Canvas; eixo Z horizontal e eixo X diâmetro vertical"
            role="img"
            data-chuck-proximity-warning={proximityWarning ? "true" : "false"}
          />
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold hover:bg-cyan-600"
              onClick={() => {
                if (visibleSegments >= payload.segments.length) updateVisibleSegments(0);
                setPlaying((current) => !current);
              }}
              aria-label={playing ? "Pausar simulação" : "Reproduzir simulação"}
            >
              {playing ? "Pausar" : "Reproduzir"}
            </button>
            <label className="flex min-w-64 flex-1 items-center gap-3 text-sm">
              <span>Passo</span>
              <input
                type="range"
                min={0}
                max={payload.segments.length}
                value={visibleSegments}
                onChange={(event) => {
                  setPlaying(false);
                  updateVisibleSegments(Number(event.target.value));
                }}
                className="w-full"
                aria-label="Selecionar passo da trajetória"
              />
              <output>{visibleSegments}/{payload.segments.length}</output>
            </label>
          </div>
        </>
      ) : (
        <div className="rounded-md border border-slate-700 bg-slate-900 p-8 text-center text-slate-300" data-empty-toolpath="true">
          Nenhum segmento disponível para simulação segura.
        </div>
      )}
    </section>
  );
}
