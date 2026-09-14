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
  tool_life_audits: [{
    schema_version: "vena-ia.cnc-tool-life-taylor-audit/v1",
    tool_id: "T0101",
    tool_material_pair: "CARBIDE_P20_P30_CARBON_STEEL",
    cutting_speed_vc_m_per_min: 180,
    taylor_n: 0.25,
    taylor_c: 350,
    effective_cutting_time_minutes: 2,
    estimated_tool_life_minutes: 14.2946,
    tool_life_consumed_percent: 13.9913,
    integrity_status: "TOOL_LIFE_SAFE",
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "TAYLOR_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_THERMAL_AND_LUBRICATION_VARIATION",
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
  }],
  cost_time_audit: {
    schema_version: "vena-ia.cnc-machining-cost-time-audit/v1",
    cost_profile: "BRL_STANDARD",
    total_cycle_time_minutes: 17.583333333,
    cutting_time_minutes: 2,
    rapid_time_minutes: 0.083333333,
    tool_change_count: 1,
    tool_change_time_minutes_each: 0.5,
    tool_change_time_minutes: 0.5,
    setup_count: 1,
    nominal_setup_time_minutes_each: 15,
    nominal_setup_time_minutes: 15,
    estimated_total_cost: 37.265362,
    machine_cost_component: 35.166666667,
    tooling_wear_cost_component: 2.098695333,
    machine_hourly_rate: 120,
    cutting_edge_cost: 15,
    currency: "BRL",
    per_tool_wear_costs: [{
      tool_id: "T0101",
      effective_cutting_time_minutes: 2,
      estimated_tool_life_minutes: 14.2946,
      consumed_fraction: 0.139913,
      cutting_edge_cost: 15,
      estimated_wear_cost: 2.098695333,
    }],
    is_theoretical_estimate: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_COST_TIME_EXCLUDES_LOGISTICS_UNPLANNED_DOWNTIME_AND_TAXES",
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
  sustainability_audit: {
    schema_version: "vena-ia.cnc-machining-sustainability-audit/v1",
    electrical_energy_kwh: 0.527778,
    cutting_energy_kwh: 0.158507,
    standby_energy_kwh: 0.369271,
    carbon_emission_kg_co2e: 0.044861,
    grid_region: "BRASIL_SIN",
    grid_emission_factor_kg_co2e_per_kwh: 0.085,
    motor_power_kw: 4.2796875,
    standby_power_kw: 1.2,
    cutting_time_minutes: 2,
    total_cycle_time_minutes: 17.583333333,
    electrical_efficiency: 0.9,
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_ENERGY_CARBON_EXCLUDES_EXTERNAL_COOLING_AND_STARTUP_PEAKS",
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

test("renders Taylor tool-life progress and mandatory note", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Vida útil teórica das ferramentas/);
  assert.match(html, /T0101/);
  assert.match(html, /VIDA ÚTIL SEGURA/);
  assert.match(html, /role="progressbar"/);
  assert.match(html, /13\.99%/);
  assert.match(html, /ESTIMATIVA ANALÍTICA DE TAYLOR - NÃO CONSIDERA FLUTUAÇÕES TÉRMICAS REAIS OU LUBRIFICAÇÃO/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders critical tool-wear warning", () => {
  const critical: MachiningTechnicalReportPayload = {
    ...report,
    tool_life_audits: [{
      ...report.tool_life_audits[0],
      tool_life_consumed_percent: 85,
      integrity_status: "TOOL_LIFE_EXHAUSTED_WARNING",
    }],
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: critical }));
  assert.match(html, /ALERTA: DESGASTE CRÍTICO/);
  assert.match(html, /aria-valuenow="85"/);
});

test("renders the analytical time and cost breakdown precisely", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Resumo econômico e de tempo/);
  assert.match(html, /17\.58 min/);
  assert.match(html, /Corte efetivo/);
  assert.match(html, /2\.00 min/);
  assert.match(html, /Avanço em vazio/);
  assert.match(html, /0\.08 min/);
  assert.match(html, /Trocas de ferramenta/);
  assert.match(html, /0\.50 min/);
  assert.match(html, /Custo de máquina/);
  assert.match(html, /BRL 35\.17/);
  assert.match(html, /Depreciação de insertos/);
  assert.match(html, /BRL 2\.10/);
  assert.match(html, /Custo total estimado/);
  assert.match(html, /BRL 37\.27/);
  assert.match(html, /ESTIMATIVA ECONÔMICA E DE TEMPO ANALÍTICA - NÃO CONSIDERA FLUTUAÇÕES LOGÍSTICAS, PARADAS NÃO PROGRAMADAS OU IMPOSTOS/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders sustainability telemetry and the informational grid selector", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Resumo ecológico e energético/);
  assert.match(html, /0\.5278 kWh/);
  assert.match(html, /0\.0449 kg CO2e/);
  assert.match(html, /Brasil · BRASIL_SIN/);
  assert.match(html, /EUA · USA_AVG/);
  assert.match(html, /Europa · EU_AVG/);
  assert.match(html, /aria-current="true"[^>]*>Brasil/);
  assert.match(html, /0\.085 kg CO2e\/kWh/);
  assert.match(html, /ESTIMATIVA ECOLÓGICA E ENERGÉTICA ANALÍTICA - NÃO CONSIDERA DINÂMICA AUXILIAR DE REFRIGERAÇÃO EXTERNA OU PICOS DE PARTIDA/);
  assert.doesNotMatch(html, /<button/i);
});
