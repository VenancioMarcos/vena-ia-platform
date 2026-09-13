import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import {
  MachiningTechnicalReportViewer,
  type MachiningTechnicalReportPayload,
} from "../src/components/cnc/MachiningTechnicalReportViewer";

const report: MachiningTechnicalReportPayload = {
  schema_version: "vena-ia.cnc-machining-report/v1",
  status: "REQUIRES_HUMAN_REVIEW",
  plan_id: "plan-report-001",
  source_plan_name: null,
  cad_job_id: "cad-report-001",
  controller_profile: "FANUC_0I",
  program_number: 9004,
  program_sha256: "a".repeat(64),
  analytical_snapshot_at: "2026-09-13T18:00:00Z",
  tools: [{ tool_id: "T0101", operations: ["ROUGH_TURNING", "FINISHING"] }],
  cycle_time_estimate: {
    total_cutting_time_seconds: 120,
    total_rapid_time_seconds: 5,
    total_cycle_time_seconds: 125,
    total_cutting_distance_mm: 40,
    total_rapid_distance_mm: 10,
    rapid_feed_rate_mm_min: 10000,
    per_tool_breakdown: [{
      tool: "T0101",
      cutting_time_seconds: 120,
      rapid_time_seconds: 5,
      cutting_distance_mm: 40,
      rapid_distance_mm: 10,
    }],
    disclaimer: "THEORETICAL_ANALYTICAL_ESTIMATE_NOT_PHYSICALLY_APPROVED",
  },
  total_distance_mm: 50,
  envelope_audit: "PASS_DECLARED_2D_ENVELOPE_ONLY",
  machine_envelope: {
    x_min_mm: 0,
    x_max_mm: 100,
    z_min_mm: -200,
    z_max_mm: 200,
    chuck_exclusion_zone: { x_min_mm: 0, x_max_mm: 100, z_min_mm: 50, z_max_mm: 100 },
  },
  chuck_proximity: {
    minimum_clearance_mm: 12.5,
    threshold_mm: 5,
    closest_segment_index: 0,
    warning_code: null,
  },
  geometry_audit: {
    schema_version: "vena-ia.cnc-geometry-dimensional-audit/v1",
    status: "PASS",
    deviations: [
      { axis: "MAX_RADIUS", nominal_mm: 26, programmed_mm: 26, signed_deviation_mm: 0, tolerance_mm: 0.001, within_tolerance: true },
      { axis: "MIN_Z", nominal_mm: -100, programmed_mm: -100, signed_deviation_mm: 0, tolerance_mm: 0.001, within_tolerance: true },
      { axis: "MAX_Z", nominal_mm: 1, programmed_mm: 1, signed_deviation_mm: 0, tolerance_mm: 0.001, within_tolerance: true },
    ],
    findings: [],
    manifest_generation_allowed: true,
  },
  coordinate_convention: "LATHE_X_DIAMETER_Z",
  governance_stamp: "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO",
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
  limitations: ["No physical validation.", "No machine authority."],
};

test("renders report metrics, tools, audit evidence, and mandatory governance", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Relatório técnico de usinagem/);
  assert.match(html, /RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO/);
  assert.match(html, /00:02:05/);
  assert.match(html, /50\.000 mm/);
  assert.match(html, /T0101/);
  assert.match(html, /ROUGH_TURNING · FINISHING/);
  assert.match(html, /PASS_DECLARED_2D_ENVELOPE_ONLY/);
  assert.match(html, /G9=PENDING_AUTHORITATIVE_REVIEW/);
  assert.match(html, /CONTROLLER_PROFILE_UNRESOLVED/);
  assert.match(html, /executable_output=false/);
  assert.match(html, /AUDITORIA GEOMÉTRICA CONFORME/);
  assert.match(html, /MAX_RADIUS/);
  assert.match(html, /Exportar laudo textual/);
  assert.match(html, /report\/download/);
});

test("contains no physical execution or machine-send controls", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.doesNotMatch(html, /<button/i);
  assert.doesNotMatch(html, /cycle start/i);
  assert.doesNotMatch(html, /enviar (?:à|a) máquina/i);
});

test("renders chuck proximity warning as an alert", () => {
  const warningReport: MachiningTechnicalReportPayload = {
    ...report,
    chuck_proximity: { ...report.chuck_proximity, minimum_clearance_mm: 4, warning_code: "WARNING_PROXIMITY_CHUCK" },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: warningReport }));
  assert.match(html, /role="alert"[^>]*>WARNING_PROXIMITY_CHUCK/);
  assert.match(html, /4\.000 mm/);
});

test("renders detected dimensional deviations without physical controls", () => {
  const rejectedReport: MachiningTechnicalReportPayload = {
    ...report,
    geometry_audit: {
      ...report.geometry_audit,
      status: "REJECTED",
      manifest_generation_allowed: false,
      findings: ["BREP_MAX_RADIUS_MISMATCH"],
      deviations: report.geometry_audit.deviations.map((item) => item.axis === "MAX_RADIUS"
        ? { ...item, programmed_mm: 27, signed_deviation_mm: 1, within_tolerance: false }
        : item),
    },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: rejectedReport }));
  assert.match(html, /DESVIO DETECTADO/);
  assert.match(html, /1\.000 mm/);
  assert.doesNotMatch(html, /<button/i);
});
