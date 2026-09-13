import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import {
  ToolpathCanvasViewer,
  type ToolpathSimulationPayload,
} from "../src/components/cnc/ToolpathCanvasViewer";


const payload: ToolpathSimulationPayload = {
  status: "SIMULATION_READY_REQUIRES_REVIEW",
  source_plan_id: "plan-sim-001",
  controller_profile: "FANUC_0I",
  coordinate_convention: "LATHE_X_DIAMETER_Z",
  machine_envelope: {
    x_min_mm: 0,
    x_max_mm: 100,
    z_min_mm: -200,
    z_max_mm: 200,
    chuck_exclusion_zone: {
      x_min_mm: 0,
      x_max_mm: 100,
      z_min_mm: 50,
      z_max_mm: 100,
    },
  },
  stock: { diameter_mm: 52, z_min_mm: -100, z_max_mm: 1 },
  chuck_proximity: { minimum_clearance_mm: 45, threshold_mm: 5, closest_segment_index: 0, warning_code: null },
  segments: [
    {
      motion_type: "RAPID",
      x_start_mm: 50,
      z_start_mm: 5,
      x_end_mm: 40,
      z_end_mm: 2,
      feed: null,
      active_tool: "T0101",
    },
    {
      motion_type: "LINEAR",
      x_start_mm: 40,
      z_start_mm: 2,
      x_end_mm: 36,
      z_end_mm: -20,
      feed: 0.2,
      active_tool: "T0101",
    },
  ],
  safety_flags: {
    physical_use_authorized: false,
    g9: "PENDING_AUTHORITATIVE_REVIEW",
    no_human_review_bypass: true,
    machine_send: false,
    dnc: false,
    nc_transfer: false,
    cycle_start: false,
    emission_status: "CONTROLLER_PROFILE_UNRESOLVED",
    executable_output: false,
  },
};


test("renders a valid simulation payload with canvas and controls", () => {
  const before = JSON.stringify(payload);
  const html = renderToStaticMarkup(createElement(ToolpathCanvasViewer, { payload }));

  assert.match(html, /<canvas/);
  assert.match(html, /eixo Z horizontal e eixo X diâmetro vertical/);
  assert.match(html, /G00 rápido/);
  assert.match(html, /G01 corte/);
  assert.match(html, /Zona da placa/);
  assert.match(html, /Reproduzir simulação/);
  assert.match(html, /Selecionar passo da trajetória/);
  assert.equal(JSON.stringify(payload), before);
});


test("preserves the mandatory audit-only governance banner", () => {
  const html = renderToStaticMarkup(createElement(ToolpathCanvasViewer, { payload }));

  assert.match(html, /AUDIT ONLY - PHYSICAL_USE_AUTHORIZED=FALSE/);
  assert.match(html, /revisão humana obrigatória/);
  assert.doesNotMatch(html, /machine.send|cycle.start|download/i);
});


test("highlights the canvas when the chuck proximity warning is active", () => {
  const warningPayload: ToolpathSimulationPayload = {
    ...payload,
    chuck_proximity: { minimum_clearance_mm: 4, threshold_mm: 5, closest_segment_index: 1, warning_code: "WARNING_PROXIMITY_CHUCK" },
  };
  const html = renderToStaticMarkup(createElement(ToolpathCanvasViewer, { payload: warningPayload }));

  assert.match(html, /data-chuck-proximity-warning="true"/);
  assert.match(html, /animate-pulse ring-2 ring-red-500/);
});


test("renders a bounded empty state without a canvas", () => {
  const emptyPayload: ToolpathSimulationPayload = { ...payload, segments: [] };
  const html = renderToStaticMarkup(createElement(ToolpathCanvasViewer, { payload: emptyPayload }));

  assert.match(html, /data-empty-toolpath="true"/);
  assert.match(html, /Nenhum segmento disponível para simulação segura/);
  assert.match(html, /AUDIT ONLY - PHYSICAL_USE_AUTHORIZED=FALSE/);
  assert.doesNotMatch(html, /<canvas/);
});
