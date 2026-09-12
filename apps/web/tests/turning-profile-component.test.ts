import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { AnalyticTurningProfile2D, TurningProfile2D } from "../components/cam/TurningProfile2D";
import { cylinderSuccess } from "./fixtures/cylinder-success";
import type { TurningToolpathPlan } from "../lib/turning-contracts";

function render(plan: TurningToolpathPlan, width = 640, height = 480): string {
  return renderToStaticMarkup(createElement(TurningProfile2D, { plan, width, height, className: "preview" }));
}

test("cylinder SSR renders every motion with its color and accessible SVG context", () => {
  const before = JSON.stringify(cylinderSuccess.plan);
  const svg = render(cylinderSuccess.plan);
  assert.match(svg, /^<svg/);
  assert.match(svg, /viewBox="0 0 640 480"/);
  assert.match(svg, /role="img"/);
  assert.match(svg, /class="preview"/);
  assert.match(svg, /Sem validação física/);
  assert.match(svg, /Z →/);
  assert.match(svg, /R ↑/);
  const lines = [...svg.matchAll(/<line\b[^>]*data-motion="([A-Z]+)"[^>]*>/g)];
  const plan: TurningToolpathPlan = cylinderSuccess.plan;
  const moves = plan.operations.flatMap(operation => operation.moves);
  assert.equal(lines.length, moves.length);
  const colors = { RAPID: "#f59e0b", CUTTING: "#06b6d4", RETRACT: "#d946ef" };
  lines.forEach(([line, motion], index) => {
    assert.equal(motion, moves[index].motion_type);
    assert.ok(line.includes(`stroke="${colors[moves[index].motion_type]}"`));
    for (const attribute of ["x1", "x2", "y1", "y2"]) {
      const match = line.match(new RegExp(`${attribute}="([^"]+)"`));
      assert.ok(match);
      assert.ok(Number.isFinite(Number(match[1])));
    }
  });
  assert.doesNotMatch(svg, /data-fallback|NaN|Infinity/);
  assert.equal(JSON.stringify(cylinderSuccess.plan), before);
  assert.equal(render(cylinderSuccess.plan), svg);
});

test("empty plan renders a neutral SVG fallback without movements", () => {
  const svg = render({ ...cylinderSuccess.plan, operations: [] });
  assert.match(svg, /data-fallback="true"/);
  assert.match(svg, /Sem trajetórias/);
  assert.doesNotMatch(svg, /data-motion/);
});

test("collapsed and nonfinite plans render fallbacks, never partial movement output", () => {
  for (const radius of [5, NaN, Infinity, -1]) {
    const plan: TurningToolpathPlan = { ...cylinderSuccess.plan, operations: [{
      operation_id: "test", operation_type: "FACING", passes_count: 1,
      moves: [{ motion_type: "CUTTING", feed_rate_type: "MM_PER_REVOLUTION", start_point: [radius, 0], end_point: [radius, 0] }],
    }] };
    const svg = render(plan);
    assert.match(svg, /data-fallback="true"/);
    assert.doesNotMatch(svg, /data-motion|NaN|Infinity/);
  }
});

test("invalid or insufficient viewports produce finite SVG fallback dimensions", () => {
  for (const [width, height] of [[0, 10], [-1, 20], [NaN, 200], [100, Infinity], [32, 32], [48, 48]]) {
    const svg = render(cylinderSuccess.plan, width, height);
    assert.match(svg, /data-fallback="true"/);
    assert.doesNotMatch(svg, /data-motion|NaN|Infinity/);
  }
});

test("a valid single-axis line remains visible", () => {
  const plan: TurningToolpathPlan = { ...cylinderSuccess.plan, operations: [{
    operation_id: "line", operation_type: "FACING", passes_count: 1,
    moves: [{ motion_type: "CUTTING", feed_rate_type: "MM_PER_REVOLUTION", start_point: [5, -10], end_point: [5, 10] }],
  }] };
  const svg = render(plan);
  assert.match(svg, /data-motion="CUTTING"/);
  assert.doesNotMatch(svg, /data-fallback/);
});

test("completed backend profile renders a review-only analytic RZ SVG and dimensions", () => {
  const html = renderToStaticMarkup(createElement(AnalyticTurningProfile2D, {
    profile: {
      points: [{ radius_mm: 12, z_mm: -30 }, { radius_mm: 12, z_mm: -10 }, { radius_mm: 6, z_mm: 0 }],
      axis_origin: [0, 0, 0], axis_direction: [0, 0, 1], is_closed: false,
    },
    boundingBox: { maxRadiusMm: 12, totalZLengthMm: 30 },
    width: 640,
    height: 400,
  }));
  assert.match(html, /Perfil 2D Analítico \(Revisão Obrigatória\)/);
  assert.match(html, /Raio máximo:.*12\.000 mm/);
  assert.match(html, /Comprimento Z:.*30\.000 mm/);
  assert.match(html, /<svg[^>]*role="img"/);
  assert.match(html, /data-profile="analytic-rz"/);
  assert.match(html, /revisão humana obrigatória/);
  assert.doesNotMatch(html, /NaN|Infinity|data-motion/);
});
