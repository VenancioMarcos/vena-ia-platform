import type { TurningToolpathPlan } from "../../lib/turning-contracts";
import { createRzProjection, getMotionColor, getRzBounds } from "../../lib/rz-projection";

type Props = Readonly<{ plan: TurningToolpathPlan; width: number; height: number; className?: string }>;

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
