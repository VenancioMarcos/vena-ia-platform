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
  surface_roughness_audit: {
    schema_version: "vena-ia.cnc-surface-roughness-audit/v1",
    ra_theoretical_um: 1.5625,
    rz_theoretical_um: 6.25,
    finish_feed_mm_per_rev: 0.2,
    insert_nose_radius_mm: 0.8,
    nominal_ra_max_um: null,
    compliance_tag: "NOMINAL_RA_TOLERANCE_UNAVAILABLE",
    model_limitation: "IDEAL_KINEMATIC_MODEL_EXCLUDES_VIBRATION_TOOL_WEAR_AND_MATERIAL_EFFECTS",
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
  },
  power_force_audit: {
    schema_version: "vena-ia.cnc-machining-power-force-audit/v1",
    material_profile: "ABNT_1045",
    kc1_1_n_per_mm2: 1900,
    kienzle_exponent_mc: 0.26,
    feed_mm_per_rev: 0.2,
    depth_of_cut_mm: 2,
    cutting_edge_angle_deg: 95,
    chip_thickness_mm: 0.19923894,
    chip_width_mm: 2.007639675,
    cutting_speed_m_per_min: 180,
    spindle_rpm_reference: 1500,
    max_spindle_rpm: 3000,
    fc_nominal_n: 1141.25,
    pc_cutting_kw: 3.42375,
    p_motor_est_kw: 4.2796875,
    mrr_cm3_min: 72,
    machine_power_limit_kw: 7.5,
    power_status: "POWER_WITHIN_LIMITS",
    spindle_efficiency: 0.8,
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "KIENZLE_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_DYNAMIC_EFFICIENCY",
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

test("renders ideal surface roughness evidence and mandatory limitation", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Ra teórico/);
  assert.match(html, /1\.563 µm/);
  assert.match(html, /Rz teórico/);
  assert.match(html, /6\.250 µm/);
  assert.match(html, /NOMINAL_RA_TOLERANCE_UNAVAILABLE/);
  assert.match(html, /RUGOSIDADE TEÓRICA CINEMÁTICA - NÃO CONSIDERA VIBRAÇÃO OU DESGASTE DA FERRAMENTA/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders Kienzle energy telemetry, governance note, and adequate badge", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Força tangencial estimada/);
  assert.match(html, /1141\.25 N/);
  assert.match(html, /3\.424 kW/);
  assert.match(html, /72\.000 cm³\/min/);
  assert.match(html, /POTÊNCIA ADEQUADA/);
  assert.match(html, /ESTIMATIVA ENERGÉTICA ANALÍTICA DE KIENZLE - NÃO CONSIDERA RENDIMENTO DINÂMICO REAL/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders the excessive-power warning badge", () => {
  const warningReport: MachiningTechnicalReportPayload = {
    ...report,
    power_force_audit: { ...report.power_force_audit, power_status: "POWER_EXCEEDED_WARNING" },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: warningReport }));
  assert.match(html, /ALERTA DE POTÊNCIA EXCESSIVA/);
});
