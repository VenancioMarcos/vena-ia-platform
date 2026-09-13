import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { SimulationWorkspace, telemetryAtStep } from "../src/components/cnc/SimulationWorkspace";
import type { ToolpathSimulationPayload } from "../src/components/cnc/ToolpathCanvasViewer";

const payload: ToolpathSimulationPayload = {
  status: "SIMULATION_READY_REQUIRES_REVIEW",
  source_plan_id: null,
  controller_profile: "FANUC_0I",
  coordinate_convention: "LATHE_X_DIAMETER_Z",
  machine_envelope: { x_min_mm: 0, x_max_mm: 100, z_min_mm: -100, z_max_mm: 100, chuck_exclusion_zone: { x_min_mm: 0, x_max_mm: 100, z_min_mm: 60, z_max_mm: 100 } },
  stock: { diameter_mm: 50, z_min_mm: -80, z_max_mm: 0 },
  segments: [
    { motion_type: "RAPID", x_start_mm: 50, z_start_mm: 5, x_end_mm: 40, z_end_mm: 2, feed: null, active_tool: "T0101" },
    { motion_type: "LINEAR", x_start_mm: 40, z_start_mm: 2, x_end_mm: 36, z_end_mm: -20, feed: 0.2, active_tool: "T0101" },
  ],
  safety_flags: { physical_use_authorized: false, g9: "PENDING_AUTHORITATIVE_REVIEW", no_human_review_bypass: true, machine_send: false, dnc: false, nc_transfer: false, cycle_start: false, emission_status: "CONTROLLER_PROFILE_UNRESOLVED", executable_output: false },
};

const blocks = ["N10 G00 X50 Z5", "N20 G00 X40 Z2", "N30 G01 X36 Z-20 F0.2"];

test("renders the integrated canvas, HUD, read-only program, and mandatory alerts", () => {
  const html = renderToStaticMarkup(createElement(SimulationWorkspace, { payload, isoBlocks: blocks }));
  assert.match(html, /Workspace integrado de simulação CNC/);
  assert.match(html, /Telemetry HUD/);
  assert.match(html, /Programa ISO — somente leitura/);
  assert.match(html, /ESTADO: AUDITORIA NÃO-EXECUTÁVEL/);
  assert.match(html, /AUDIT ONLY - PHYSICAL_USE_AUTHORIZED=FALSE/);
  assert.match(html, /G9=PENDING_AUTHORITATIVE_REVIEW/);
});

test("maps each scrub step to synchronized endpoint telemetry and ISO block", () => {
  assert.deepEqual(telemetryAtStep(payload, blocks, 0), { xDiameterMm: 50, zMm: 5, feed: null, activeTool: "T0101", isoBlock: blocks[0] });
  assert.deepEqual(telemetryAtStep(payload, blocks, 1), { xDiameterMm: 40, zMm: 2, feed: null, activeTool: "T0101", isoBlock: blocks[1] });
  assert.deepEqual(telemetryAtStep(payload, blocks, 2), { xDiameterMm: 36, zMm: -20, feed: 0.2, activeTool: "T0101", isoBlock: blocks[2] });
});

test("bounds out-of-range scrub steps defensively", () => {
  assert.equal(telemetryAtStep(payload, blocks, 999).isoBlock, blocks[2]);
  assert.equal(telemetryAtStep(payload, blocks, -4).isoBlock, blocks[0]);
});

test("renders a safe error fallback without operational controls", () => {
  const html = renderToStaticMarkup(createElement(SimulationWorkspace, { error: "PAYLOAD_UNAVAILABLE" }));
  assert.match(html, /Simulação indisponível: PAYLOAD_UNAVAILABLE/);
  assert.match(html, /ESTADO: AUDITORIA NÃO-EXECUTÁVEL/);
  assert.doesNotMatch(html, /Reproduzir simulação/);
});
