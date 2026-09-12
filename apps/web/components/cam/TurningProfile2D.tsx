import type { TurningProfile2D as TurningProfileData, TurningToolpathPlan } from "../../lib/turning-contracts";
import { createRzProjection, getMotionColor, getRzBounds } from "../../lib/rz-projection";

type Props = Readonly<{ plan: TurningToolpathPlan; width: number; height: number; className?: string }>;
type AnalyticProps = Readonly<{
  profile: TurningProfileData;
  boundingBox: Readonly<{ maxRadiusMm: number; totalZLengthMm: number }>;
  width: number;
  height: number;
  className?: string;
}>;

/** Review-only profile returned by the authenticated STEP ingestion API. */
export function AnalyticTurningProfile2D({ profile, boundingBox, width, height, className }: AnalyticProps) {
  let drawing;
  let fallback = "";
  try {
    const bounds = getRzBounds(profile);
    if (!bounds || profile.points.length < 2) {
      fallback = "Perfil analítico insuficiente para visualização";
    } else {
      const projection = createRzProjection(bounds, { width, height, padding: 24 });
      const points = profile.points.map(point => projection.project([point.radius_mm, point.z_mm]).join(",")).join(" ");
      drawing = <>
        <g stroke="#64748b" strokeWidth="1" fill="none" aria-label="Direções dos eixos">
          <line x1="12" y1={height - 12} x2={width - 12} y2={height - 12} />
          <line x1="12" y1={height - 12} x2="12" y2="12" />
        </g>
        <g fill="#cbd5e1" fontSize="11">
          <text x={width - 12} y={height - 16} textAnchor="end">Z →</text>
          <text x="16" y="16">R ↑</text>
        </g>
        <polyline data-profile="analytic-rz" points={points} fill="none" stroke="#22d3ee"
          strokeWidth="2" vectorEffect="non-scaling-stroke" />
      </>;
    }
  } catch {
    fallback = "Não foi possível projetar o perfil analítico";
  }

  return <div className={className} aria-label="Resultado do perfil STEP processado">
    <span className="inline-flex rounded bg-amber-900 px-2 py-1 text-xs font-medium text-amber-100">
      Perfil 2D Analítico (Revisão Obrigatória)
    </span>
    <dl className="mt-2 grid gap-1 text-sm text-slate-200 sm:grid-cols-2">
      <div><dt className="inline text-slate-400">Raio máximo: </dt><dd className="inline">{boundingBox.maxRadiusMm.toFixed(3)} mm</dd></div>
      <div><dt className="inline text-slate-400">Comprimento Z: </dt><dd className="inline">{boundingBox.totalZLengthMm.toFixed(3)} mm</dd></div>
    </dl>
    <svg xmlns="http://www.w3.org/2000/svg" role="img"
      aria-label={fallback || "Perfil RZ analítico — revisão humana obrigatória"}
      width={width} height={height} viewBox={`0 0 ${width} ${height}`}
      className="mt-3 h-auto max-w-full rounded" preserveAspectRatio="xMidYMid meet">
      <title>Perfil STEP analítico RZ</title>
      <desc>Raio R em função de Z. Visualização analítica sujeita a revisão, sem autorização física.</desc>
      <rect width="100%" height="100%" fill="#0f172a" />
      {fallback ? <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle"
        fill="#cbd5e1" fontSize="12" data-fallback="true">{fallback}</text> : drawing}
    </svg>
  </div>;
}

/** Synthetic inspection only. No machine commands, state, effects or network. */
export function TurningProfile2D({ plan, width, height, className }: Props) {
  const validSize = Number.isFinite(width) && width > 0 && Number.isFinite(height) && height > 0;
  const canvasWidth = validSize ? width : 320;
  const canvasHeight = validSize ? height : 180;
  let drawing;
  let fallback = "";
  try {
    if (!validSize) throw new RangeError("Invalid viewport");
    const bounds = getRzBounds(null, [plan]);
    if (!bounds) {
      fallback = "Sem trajetórias para visualizar";
    } else if (bounds.minR === bounds.maxR && bounds.minZ === bounds.maxZ) {
      fallback = "Trajetória sem extensão para visualizar";
    } else {
      const projection = createRzProjection(bounds, { width, height, padding: 24 });
      const segments = plan.operations.flatMap((operation, operationIndex) => operation.moves.map((move, moveIndex) => ({
        key: `${operationIndex}-${moveIndex}`,
        start: projection.project(move.start_point), end: projection.project(move.end_point),
        color: getMotionColor(move.motion_type), motion: move.motion_type,
      })));
      drawing = <>
        <g stroke="#64748b" strokeWidth="1" fill="none" aria-label="Direções dos eixos">
          <line x1="12" y1={height - 12} x2={width - 12} y2={height - 12} />
          <line x1="12" y1={height - 12} x2="12" y2="12" />
        </g>
        <g fill="#cbd5e1" fontSize="11">
          <text x={width - 12} y={height - 16} textAnchor="end">Z →</text>
          <text x="16" y="16">R ↑</text>
        </g>
        <g fill="none" strokeWidth="1.5" aria-label="Movimentos sintéticos">
          {segments.map(segment => <line key={segment.key} data-motion={segment.motion}
            x1={segment.start[0]} y1={segment.start[1]} x2={segment.end[0]} y2={segment.end[1]}
            stroke={segment.color} vectorEffect="non-scaling-stroke">
            <title>{segment.motion}</title>
          </line>)}
        </g>
      </>;
    }
  } catch {
    fallback = "Não foi possível projetar a trajetória";
  }
  return <svg xmlns="http://www.w3.org/2000/svg" role="img"
    aria-label={fallback || "Trajetória sintética de torneamento — sem autorização física"}
    width={canvasWidth} height={canvasHeight} viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
    className={className} preserveAspectRatio="xMidYMid meet">
    <title>Inspeção sintética RZ</title>
    <desc>Raio R em escala proporcional a Z. Cores: avanço rápido âmbar, corte ciano, recuo magenta. Eixos indicam direções, não a origem da peça. Sem validação física.</desc>
    <rect width="100%" height="100%" fill="#0f172a" />
    {fallback ? <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle"
      fill="#cbd5e1" fontSize="12" data-fallback="true">{fallback}</text> : drawing}
  </svg>;
}
