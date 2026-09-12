import assert from "node:assert/strict";
import { test } from "node:test";
import { createRzProjection, getMotionColor, getRzBounds } from "../lib/rz-projection";
import type { TurningProfile2D, TurningToolpathPlan } from "../lib/turning-contracts";
import { cylinderSuccess } from "./fixtures/cylinder-success";

test("cylinder profile extremes fit a centered, radius-based viewport", () => {
  const bounds = getRzBounds(cylinderSuccess.profile);
  assert.deepStrictEqual(bounds, { minR: 0, maxR: 25, minZ: -100, maxZ: 0 });
  const view = createRzProjection(bounds, { width: 240, height: 140, padding: 20 });
  assert.equal(view.scale, 2);
  assert.deepStrictEqual(view.project([0, -100]), [20, 95]);
  assert.deepStrictEqual(view.project([25, 0]), [220, 45]);
});

test("metric scale is equal on both axes and radial growth points upward", () => {
  const view = createRzProjection(getRzBounds(cylinderSuccess.profile), { width: 300, height: 200, padding: 10 });
  const origin = view.project([0, -100]);
  const radial = view.project([10, -100]);
  const axial = view.project([0, -90]);
  assert.ok(radial[1] < origin[1]);
  assert.ok(axial[0] > origin[0]);
  assert.equal(origin[1] - radial[1], axial[0] - origin[0]);
  assert.equal(axial[0] - origin[0], 10 * view.scale);
});

test("all nominal and quantized endpoints fit inside the requested padding", () => {
  const plans = [cylinderSuccess.plan, cylinderSuccess.quantized_plan];
  const view = createRzProjection(getRzBounds(cylinderSuccess.profile, plans), { width: 640, height: 480, padding: 24 });
  for (const plan of plans) for (const operation of plan.operations) for (const move of operation.moves) {
    for (const point of [move.start_point, move.end_point]) {
      const [x, y] = view.project(point);
      assert.ok(x >= 24 - 1e-9 && x <= 616 + 1e-9);
      assert.ok(y >= 24 - 1e-9 && y <= 456 + 1e-9);
    }
  }
});

test("unordered stepped profile and every motion expand bounds without mutating inputs", () => {
  const profile: TurningProfile2D = { ...cylinderSuccess.profile, points: [
    { radius_mm: 30, z_mm: -20 }, { radius_mm: 10, z_mm: -70 }, { radius_mm: 20, z_mm: 5 },
  ] };
  const plan: TurningToolpathPlan = { ...cylinderSuccess.plan, operations: [{
    operation_id: "test", operation_type: "ROUGH_TURNING", passes_count: 1,
    moves: [
      { motion_type: "RAPID", start_point: [40, 10], end_point: [30, 10], feed_rate_type: "MM_PER_MINUTE" },
      { motion_type: "CUTTING", start_point: [30, 10], end_point: [30, -80], feed_rate_type: "MM_PER_MINUTE" },
      { motion_type: "RETRACT", start_point: [30, -80], end_point: [50, -90], feed_rate_type: "MM_PER_MINUTE" },
    ],
  }] };
  const before = JSON.stringify({ profile, plan });
  assert.deepStrictEqual(getRzBounds(profile, [plan]), { minR: 10, maxR: 50, minZ: -90, maxZ: 10 });
  assert.deepStrictEqual(getRzBounds(null, [plan]), { minR: 30, maxR: 50, minZ: -90, maxZ: 10 });
  assert.equal(JSON.stringify({ profile, plan }), before);
});

test("empty input has an explicit unit-window fallback", () => {
  assert.equal(getRzBounds(null), null);
  assert.equal(getRzBounds({ ...cylinderSuccess.profile, points: [] }), null);
  const view = createRzProjection(null, { width: 100, height: 100, padding: 0 });
  assert.deepStrictEqual(view.project([0, 0]), [0, 100]);
  assert.deepStrictEqual(view.project([1, 1]), [100, 0]);
});

test("a single point is centered with a finite scale", () => {
  const view = createRzProjection({ minR: 5, maxR: 5, minZ: -7, maxZ: -7 }, { width: 100, height: 80, padding: 10 });
  assert.equal(view.scale, 60);
  assert.deepStrictEqual(view.project([5, -7]), [50, 40]);
});

test("horizontal and vertical zero-area lines retain their measurable extent", () => {
  const horizontal = createRzProjection({ minR: 5, maxR: 5, minZ: -10, maxZ: 10 }, { width: 100, height: 80, padding: 10 });
  assert.deepStrictEqual(horizontal.project([5, -10]), [10, 40]);
  assert.deepStrictEqual(horizontal.project([5, 10]), [90, 40]);
  const vertical = createRzProjection({ minR: 0, maxR: 20, minZ: 3, maxZ: 3 }, { width: 100, height: 80, padding: 10 });
  assert.deepStrictEqual(vertical.project([0, 3]), [50, 70]);
  assert.deepStrictEqual(vertical.project([20, 3]), [50, 10]);
});

test("invalid bounds and viewport values fail explicitly", () => {
  for (const bounds of [
    { minR: -1, maxR: 1, minZ: 0, maxZ: 1 },
    { minR: 2, maxR: 1, minZ: 0, maxZ: 1 },
    { minR: 0, maxR: 1, minZ: 2, maxZ: 1 },
    { minR: 0, maxR: NaN, minZ: 0, maxZ: 1 },
    { minR: 0, maxR: 1, minZ: -Number.MAX_VALUE, maxZ: Number.MAX_VALUE },
  ]) assert.throws(() => createRzProjection(bounds, { width: 100, height: 100 }), RangeError);
  for (const viewport of [
    { width: 0, height: 100 }, { width: 100, height: Infinity },
    { width: 100, height: 100, padding: -1 }, { width: 100, height: 100, padding: 50 },
    { width: 100, height: 100, padding: NaN },
  ]) assert.throws(() => createRzProjection(null, viewport), RangeError);
});

test("nonfinite coordinates, negative radius and unrepresentable scale are rejected", () => {
  for (const [r, z] of [[NaN, 0], [0, Infinity], [-1, 0]]) {
    assert.throws(() => getRzBounds({ ...cylinderSuccess.profile, points: [{ radius_mm: r, z_mm: z }] }), RangeError);
    assert.throws(() => createRzProjection(null, { width: 100, height: 100 }).project([r, z]), RangeError);
  }
  assert.throws(() => createRzProjection({ minR: 0, maxR: Number.MIN_VALUE, minZ: 0, maxZ: 0 }, { width: 100, height: 100 }), RangeError);
  const view = createRzProjection(null, { width: 100, height: 100 });
  assert.throws(() => view.project([Number.MAX_VALUE, Number.MAX_VALUE]), RangeError);
});

test("projection snapshots bounds and does not clamp out-of-bounds points", () => {
  const bounds = { minR: 0, maxR: 10, minZ: 0, maxZ: 10 };
  const view = createRzProjection(bounds, { width: 100, height: 100, padding: 0 });
  bounds.minZ = -100;
  assert.deepStrictEqual(view.project([5, 5]), [50, 50]);
  assert.deepStrictEqual(view.project([5, 20]), [200, 50]);
  assert.equal(view.bounds.minZ, 0);
});

test("motion colors distinguish rapid, cutting and retract", () => {
  assert.equal(getMotionColor("RAPID"), "#f59e0b");
  assert.equal(getMotionColor("CUTTING"), "#06b6d4");
  assert.equal(getMotionColor("RETRACT"), "#d946ef");
});

test("near-zero coordinates preserve metric offsets within 1e-9 pixels", () => {
  const view = createRzProjection({ minR: 0, maxR: 1, minZ: -1, maxZ: 1 }, { width: 220, height: 120, padding: 10 });
  for (const delta of [0, 1e-12, 1e-9, 1e-6]) {
    const [x, y] = view.project([delta, delta]);
    assert.ok(Math.abs(x - (110 + delta * 100)) <= 1e-9);
    assert.ok(Math.abs(y - (110 - delta * 100)) <= 1e-9);
  }
});

test("screen coordinates recover engineering coordinates within 1e-10 mm", () => {
  const bounds = { minR: 0, maxR: 37.125, minZ: -103.75, maxZ: 4.5 };
  const view = createRzProjection(bounds, { width: 731, height: 389, padding: 17.25 });
  const anchor = view.project([bounds.minR, bounds.minZ]);
  for (const r of [0, 1e-12, 12.3456789, 37.125]) for (const z of [-103.75, -1e-12, 0, 4.5]) {
    const [x, y] = view.project([r, z]);
    assert.ok(Math.abs(bounds.minZ + (x - anchor[0]) / view.scale - z) <= 1e-10);
    assert.ok(Math.abs(bounds.minR + (anchor[1] - y) / view.scale - r) <= 1e-10);
  }
});

test("near-zero single lines remain centered without inventing radial or axial span", () => {
  const horizontal = createRzProjection({ minR: 0, maxR: 0, minZ: -1e-9, maxZ: 1e-9 }, { width: 3, height: 3, padding: 1 });
  const vertical = createRzProjection({ minR: 0, maxR: 2e-9, minZ: 0, maxZ: 0 }, { width: 3, height: 3, padding: 1 });
  for (const [actual, expected] of [
    [horizontal.project([0, -1e-9]), [1, 1.5]],
    [horizontal.project([0, 1e-9]), [2, 1.5]],
    [vertical.project([0, 0]), [1.5, 2]],
    [vertical.project([2e-9, 0]), [1.5, 1]],
  ]) actual.forEach((value, index) => assert.ok(Math.abs(value - expected[index]) <= 1e-12));
});

test("low-resolution padding boundary fails explicitly and just-below remains finite", () => {
  for (const size of [1, 2, 16, 32]) {
    for (const padding of [size / 2, size, Number.MAX_VALUE]) {
      assert.throws(() => createRzProjection(null, { width: size, height: size, padding }), RangeError);
    }
    const padding = size / 2 - 1e-6;
    const view = createRzProjection(null, { width: size, height: size, padding });
    for (const point of [view.project([0, 0]), view.project([1, 1])]) {
      point.forEach(value => {
        assert.ok(Number.isFinite(value));
        assert.ok(value >= padding - 1e-12 && value <= size - padding + 1e-12);
      });
    }
  }
  assert.throws(() => createRzProjection(null, { width: 16, height: 16 }), RangeError);
});
