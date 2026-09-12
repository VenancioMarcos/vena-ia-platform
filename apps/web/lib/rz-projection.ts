import type { TurningPoint2D, TurningProfile2D, TurningToolpathMove, TurningToolpathPlan } from "./turning-contracts";

export type RzBounds = Readonly<{ minR: number; maxR: number; minZ: number; maxZ: number }>;
export type RzViewport = Readonly<{ width: number; height: number; padding?: number }>;
export type ScreenPoint = readonly [x: number, y: number];
export type RzProjection = Readonly<{
  scale: number;
  bounds: RzBounds;
  project: (point: TurningPoint2D) => ScreenPoint;
}>;

function checkPoint([r, z]: TurningPoint2D): void {
  if (!Number.isFinite(r) || r < 0 || !Number.isFinite(z)) {
    throw new RangeError("RZ coordinates must be finite and radius non-negative");
  }
}

/** Includes all motions; no geometry, collision or physical-authority validation. */
export function getRzBounds(profile: TurningProfile2D | null, plans: readonly TurningToolpathPlan[] = []): RzBounds | null {
  let bounds: RzBounds | null = null;
  const include = (point: TurningPoint2D): void => {
    checkPoint(point);
    const [r, z] = point;
    bounds = bounds === null ? { minR: r, maxR: r, minZ: z, maxZ: z } : {
      minR: Math.min(bounds.minR, r), maxR: Math.max(bounds.maxR, r),
      minZ: Math.min(bounds.minZ, z), maxZ: Math.max(bounds.maxZ, z),
    };
  };
  for (const point of profile?.points ?? []) include([point.radius_mm, point.z_mm]);
  for (const plan of plans) {
    for (const operation of plan.operations) {
      for (const move of operation.moves) {
        include(move.start_point);
        include(move.end_point);
      }
    }
  }
  return bounds;
}

/** Pixel-only fit: x follows Z, y opposes R; R remains radius, never diameter. */
export function createRzProjection(input: RzBounds | null, viewport: RzViewport): RzProjection {
  // Copy/freeze the bounds so later caller mutation cannot change this transform.
  const bounds = Object.freeze({ ...(input ?? { minR: 0, maxR: 1, minZ: 0, maxZ: 1 }) });
  const { width, height, padding = 16 } = viewport;
  checkPoint([bounds.minR, bounds.minZ]);
  checkPoint([bounds.maxR, bounds.maxZ]);
  const spanR = bounds.maxR - bounds.minR;
  const spanZ = bounds.maxZ - bounds.minZ;
  const availableWidth = width - 2 * padding;
  const availableHeight = height - 2 * padding;
  if (![width, height, padding, availableWidth, availableHeight, spanR, spanZ].every(Number.isFinite) ||
      padding < 0 || availableWidth <= 0 || availableHeight <= 0 || spanR < 0 || spanZ < 0) {
    throw new RangeError("Invalid RZ bounds or viewport/padding");
  }
  const scale = spanR === 0 && spanZ === 0 ? Math.min(availableWidth, availableHeight) :
    Math.min(spanZ === 0 ? Infinity : availableWidth / spanZ, spanR === 0 ? Infinity : availableHeight / spanR);
  if (!Number.isFinite(scale) || scale <= 0) throw new RangeError("Unrepresentable projection scale");
  const left = padding + (availableWidth - spanZ * scale) / 2;
  const bottom = height - padding - (availableHeight - spanR * scale) / 2;
  return Object.freeze({
    scale, bounds,
    project(point: TurningPoint2D): ScreenPoint {
      checkPoint(point);
      const x = left + (point[1] - bounds.minZ) * scale;
      const y = bottom - (point[0] - bounds.minR) * scale;
      if (!Number.isFinite(x) || !Number.isFinite(y)) throw new RangeError("Unrepresentable screen coordinate");
      // No clipping: points outside the fitted bounds may fall outside the viewport.
      return [x, y];
    },
  });
}

export function getMotionColor(motion: TurningToolpathMove["motion_type"]): string {
  switch (motion) {
    case "RAPID": return "#f59e0b";
    case "CUTTING": return "#06b6d4";
    case "RETRACT": return "#d946ef";
    default: throw new RangeError(`Unsupported motion: ${String(motion)}`);
  }
}
