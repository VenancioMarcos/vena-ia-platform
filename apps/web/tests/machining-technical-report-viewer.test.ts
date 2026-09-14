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
  stability_audits: [{
    schema_version: "vena-ia.cnc-machining-stability-audit/v1",
    tool_id: "T0101",
    tool_overhang_mm: 60,
    tool_diameter_mm: 20,
    overhang_ratio_l_d: 3,
    young_modulus_mpa: 210000,
    second_moment_area_mm4: 7853.981633974,
    equivalent_stiffness_n_per_mm: 22907.446432426,
    cutting_force_n: 1141.25,
    static_deflection_um: 49.820044472,
    specific_cutting_pressure_n_per_mm2: 1900,
    frf_real_compliance_mm_per_n: 0.0005,
    depth_of_cut_mm: 0.5,
    stability_limit_depth_mm: 0.526315789,
    stability_status: "DYNAMICALLY_STABLE",
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_STABILITY_EXCLUDES_WORKPIECE_AND_SPINDLE_VIBRATION_MODES",
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
  parameter_optimizations: [{
    schema_version: "vena-ia.cnc-machining-parameter-optimization/v1",
    tool_id: "T0101",
    material_profile: "ABNT_1045",
    programmed_vc_m_min: 180,
    programmed_feed_mm_rev: 0.2,
    programmed_ap_mm: 0.5,
    vc_min_m_min: 90,
    vc_max_m_min: 225,
    feed_min_mm_rev: 0.1,
    feed_max_mm_rev: 0.25,
    ap_min_mm: 0.25,
    ap_max_mm: 0.625,
    target_ra_um: 1.5625,
    insert_nose_radius_mm: 0.8,
    cutting_edge_angle_deg: 95,
    machine_power_limit_kw: 7.5,
    stability_limit_depth_mm: 0.526315789,
    overhang_ratio_l_d: 3,
    recommended_vc_m_min: 225,
    recommended_feed_mm_rev: 0.2,
    recommended_ap_mm: 0.526315789,
    predicted_mrr_cm3_min: 23.684210505,
    predicted_motor_power_kw: 1.407521,
    predicted_ra_um: 1.5625,
    predicted_tool_life_minutes: 5.855967078,
    optimization_status: "OPTIMAL_TRADE_OFF_FOUND",
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_CUTTING_PARAMETERS_REQUIRE_MANUAL_PROCESS_ENGINEERING_APPROVAL",
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
  risk_matrix: {
    schema_version: "vena-ia.cnc-machining-risk-matrix/v1",
    envelope_audit: "PASS_DECLARED_2D_ENVELOPE_ONLY",
    geometry_audit_status: "PASS",
    geometry_manifest_generation_allowed: true,
    minimum_chuck_clearance_mm: 12.5,
    chuck_proximity_threshold_mm: 5,
    chuck_proximity_warning: false,
    max_overhang_ratio_l_d: 3,
    dynamic_warning_present: false,
    required_motor_power_kw: 4.2796875,
    machine_power_limit_kw: 7.5,
    power_warning_present: false,
    max_tool_life_consumed_percent: 13.9913,
    tool_wear_warning_present: false,
    overall_risk_score: 0,
    risk_level: "LOW_RISK",
    dimensional_risk_score: 0,
    dynamic_risk_score: 0,
    energy_risk_score: 0,
    tool_wear_risk_score: 0,
    mitigation_recommendations: [
      "Manter revisão humana e homologação de processo antes de qualquer aplicação física.",
    ],
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "CONSOLIDATED_ANALYTICAL_RISK_MATRIX_IS_PRELIMINARY_AND_NOT_AN_EXPERT_REPORT",
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
  process_sheet: {
    schema_version: "vena-ia.cnc-machining-process-sheet/v1",
    part_id: "cad-report-001",
    revision: "ANALYTICAL-1",
    source_plan_id: "plan-report-001",
    source_cam_plan: {
      status: "PLANNED_REQUIRES_REVIEW",
      operation_type: "ROUGH_TURNING",
      passes: [{
        sequence: 1,
        operation_type: "ROUGH_TURNING",
        coordinates_rz_mm: [{ r_mm: 26, z_mm: 1 }, { r_mm: 25, z_mm: -100 }],
        estimated_removed_volume_mm3: 1000,
      }],
      material_removal_volume_mm3: 1000,
      warnings: ["ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW"],
      executable_output: false,
      physical_use_authorized: false,
      g9_status: "PENDING_AUTHORITATIVE_REVIEW",
      emission_status: "CONTROLLER_PROFILE_UNRESOLVED",
    },
    source_stock: { diameter_mm: 52, z_min_mm: -100, z_max_mm: 1 },
    source_machine_envelope: {
      x_min_mm: 0,
      x_max_mm: 100,
      z_min_mm: -200,
      z_max_mm: 200,
      chuck_exclusion_zone: { x_min_mm: 0, x_max_mm: 100, z_min_mm: 50, z_max_mm: 100 },
    },
    source_chuck_proximity: {
      minimum_clearance_mm: 12.5,
      threshold_mm: 5,
      closest_segment_index: 0,
      warning_code: null,
    },
    source_cycle_time_estimate: {
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
    raw_stock_dimensions: { diameter_mm: 52, axial_length_mm: 101, z_min_mm: -100, z_max_mm: 1 },
    clamping_setup: {
      setup_type: "DECLARED_CHUCK_ENVELOPE_REQUIRES_MANUAL_SETUP",
      chuck_exclusion_zone: { x_min_mm: 0, x_max_mm: 100, z_min_mm: 50, z_max_mm: 100 },
      minimum_clearance_mm: 12.5,
      proximity_threshold_mm: 5,
      estimated_setup_time_min: 15,
      clamping_instruction: "CONFIRM_CHUCK_CONTACT_AND_STOCK_PROJECTION_MANUALLY_BEFORE_PROCESS_APPROVAL",
      balance_requirement: "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED",
    },
    sequence_operations: [
      {
        sequence: 1,
        operation_id: "OP010",
        phase: "SETUP",
        source_pass_sequence: null,
        tool_id: null,
        tool_description: null,
        insert_reference: null,
        cutting_speed_vc_m_per_min: null,
        feed_mm_per_rev: null,
        depth_of_cut_ap_mm: null,
        spindle_rpm: null,
        feed_rate_mm_min: null,
        estimated_time_min: 15,
        fixture_requirement: "USE_DECLARED_CHUCK_ENVELOPE_AND_VERIFY_CLEARANCE_MANUALLY",
        balance_requirement: "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED",
      },
      {
        sequence: 2,
        operation_id: "OP020",
        phase: "ROUGH_TURNING",
        source_pass_sequence: 1,
        tool_id: "T0101",
        tool_description: "ROUGHING TOOL",
        insert_reference: "INSERT_R0.800_RIGHT_HAND",
        cutting_speed_vc_m_per_min: 180,
        feed_mm_per_rev: 0.2,
        depth_of_cut_ap_mm: 2,
        spindle_rpm: 1500,
        feed_rate_mm_min: 300,
        estimated_time_min: 2.083333333,
        fixture_requirement: "USE_DECLARED_CHUCK_ENVELOPE_AND_VERIFY_CLEARANCE_MANUALLY",
        balance_requirement: "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED",
      },
    ],
    total_operations_count: 2,
    estimated_total_time_min: 17.083333333,
    safety_instructions: [
      "Confirmar manualmente a fixação, a projeção do material e a folga em relação à placa.",
      "Conferir ferramenta, inserto, corretores e parâmetros com a engenharia de processos.",
      "Submeter a folha ao preparador de máquinas; este documento não concede permissão física.",
    ],
    is_theoretical_sheet: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_PROCESS_SHEET_REQUIRES_MACHINE_SETUP_APPROVAL",
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
  residual_stock_audit: {
    schema_version: "vena-ia.cnc-residual-stock-audit/v1",
    source_plan_id: "plan-report-001",
    source_cam_plan: {
      status: "PLANNED_REQUIRES_REVIEW",
      operation_type: "ROUGH_TURNING",
      passes: [{
        sequence: 1,
        operation_type: "ROUGH_TURNING",
        coordinates_rz_mm: [{ r_mm: 26, z_mm: 1 }, { r_mm: 25, z_mm: -100 }],
        estimated_removed_volume_mm3: 1000,
      }],
      material_removal_volume_mm3: 1000,
      warnings: ["ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW"],
      executable_output: false,
      physical_use_authorized: false,
      g9_status: "PENDING_AUTHORITATIVE_REVIEW",
      emission_status: "CONTROLLER_PROFILE_UNRESOLVED",
    },
    source_nominal_profile: [
      { r_mm: 0, z_mm: 1 },
      { r_mm: 26, z_mm: 1 },
      { r_mm: 25.5, z_mm: 1 },
      { r_mm: 25.5, z_mm: -100 },
      { r_mm: 0, z_mm: -100 },
    ],
    stock_radius_mm: 26,
    finish_allowance_nominal_mm: 0,
    linear_tolerance_mm: 0.001,
    tool_cutting_edge_length_mm: 12,
    sections: [{
      front_z_mm: 1,
      rear_z_mm: -100,
      nominal_radius_mm: 25.5,
      in_process_radius_mm: 25.5,
      residual_stock_mm: 0,
    }],
    max_residual_stock_mm: 0,
    min_residual_stock_mm: 0,
    average_stock_allowance_mm: 0,
    gouging_detected: false,
    status: "UNIFORM_ALLOWANCE_COMPLIANT",
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_RESIDUAL_STOCK_AUDIT_DOES_NOT_REPLACE_PHYSICAL_CMM_MEASUREMENT",
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
  part_elastic_deflection_audit: {
    schema_version: "vena-ia.cnc-part-elastic-deflection-audit/v1",
    part_unsupported_length_mm: 101,
    minimum_diameter_mm: 51,
    radial_cutting_force_n: 570.625,
    young_modulus_mpa: 210000,
    second_moment_area_mm4: 332086.0275259113,
    calculated_stiffness_n_per_mm: 203061.23874607915,
    radial_tolerance_mm: 0.02,
    max_deflection_um: 2.8101128680375393,
    deflection_status: "ELASTIC_DEFLECTION_COMPLIANT",
    theoretical: true,
    physical: false,
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_PART_DEFLECTION_EXCLUDES_TAILSTOCK_AND_STEADY_REST_SUPPORT",
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
  spindle_power_torque_envelope_audit: {
    schema_version: "vena-ia.cnc-spindle-power-torque-envelope-audit/v2",
    spindle_rpm_min: 150,
    spindle_rpm_max: 3000,
    curve_points: [
      { spindle_rpm: 150, available_torque_nm: 47.746482928, available_power_kw: 0.75 },
      { spindle_rpm: 1500, available_torque_nm: 47.746482928, available_power_kw: 7.5 },
      { spindle_rpm: 3000, available_torque_nm: 23.873241464, available_power_kw: 7.5 },
    ],
    operating_points: [{
      spindle_rpm: 1500,
      required_cutting_power_kw: 3.42375,
      required_torque_nm: 21.796043104,
      available_power_kw: 7.5,
      available_torque_nm: 47.746482928,
      power_margin_kw: 4.07625,
      power_margin_percent: 54.35,
      torque_margin_nm: 25.950439824,
      status: "WITHIN_POWER_TORQUE_ENVELOPE",
    }],
    audit_status: "POWER_TORQUE_ENVELOPE_COMPLIANT",
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "DECLARED_SPINDLE_POWER_TORQUE_CURVE_REQUIRES_MACHINE_PROFILE_VALIDATION",
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
  thermal_expansion_drift_audit: {
    schema_version: "vena-ia.cnc-thermal-expansion-drift-audit/v2",
    material_profile: "ABNT_1045",
    linear_expansion_coefficient_per_c: 0.000012,
    spindle_expansion_coefficient_per_c: 0.000012,
    reference_temperature_c: 20,
    workpiece_mean_temperature_c: 40,
    spindle_mean_temperature_c: 35,
    workpiece_mean_temperature_rise_c: 20,
    spindle_mean_temperature_rise_c: 15,
    workpiece_axial_reference_length_mm: 101,
    workpiece_diameter_reference_mm: 52,
    spindle_z_reference_length_mm: 150,
    workpiece_z_expansion_um: 24.24,
    workpiece_x_expansion_um: 6.24,
    spindle_z_drift_um: 27,
    total_z_axis_drift_um: 51.24,
    total_x_axis_drift_um: 6.24,
    z_axis_tolerance_um: 100,
    x_axis_tolerance_um: 100,
    audit_status: "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE",
    theoretical: true,
    physical: false,
    is_theoretical_model: true,
    physical_use_authorized: false,
    model_limitation: "ANALYTICAL_THERMAL_DRIFT_EXCLUDES_TRANSIENT_GRADIENTS_COOLANT_AND_MACHINE_COMPENSATION",
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

test("renders stable rigidity telemetry and the mandatory dynamic limitation", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Rigidez e estabilidade dinâmica/);
  assert.match(html, /Relação de balanço L\/D/);
  assert.match(html, /3\.00/);
  assert.match(html, /49\.820 µm/);
  assert.match(html, /22907\.45 N\/mm/);
  assert.match(html, /SISTEMA ESTÁVEL/);
  assert.match(html, /ESTIMATIVA ANALÍTICA DE ESTABILIDADE DINÂMICA - NÃO CONSIDERA MODOS DE VIBRAÇÃO DA PEÇA OU DO FUSO/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders the chatter high-risk warning badge", () => {
  const warningReport: MachiningTechnicalReportPayload = {
    ...report,
    stability_audits: [{
      ...report.stability_audits[0],
      tool_overhang_mm: 100,
      overhang_ratio_l_d: 5,
      equivalent_stiffness_n_per_mm: 4948.008429404,
      static_deflection_um: 230.648359603,
      stability_status: "CHATTER_HIGH_RISK_WARNING",
    }],
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: warningReport }));
  assert.match(html, /ALERTA: RISCO DE CHATTER \(L\/D CRÍTICO\)/);
});

test("renders programmed and recommended parameters with manual-approval governance", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Otimização multicritério de parâmetros/);
  assert.match(html, /COMPROMISSO ANALÍTICO ÓTIMO ENCONTRADO/);
  assert.match(html, /180\.000 m\/min/);
  assert.match(html, /225\.000 m\/min/);
  assert.match(html, /23\.684 cm³\/min/);
  assert.match(html, /SUGESTÃO ANALÍTICA DE PARÂMETROS DE CORTE - APLICAÇÃO EM MÁQUINA REQUER HOMOLOGAÇÃO MANUAL POR ENGENHARIA DE PROCESSOS/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders infeasible constraints without any automatic override control", () => {
  const infeasible: MachiningTechnicalReportPayload = {
    ...report,
    parameter_optimizations: [{
      ...report.parameter_optimizations[0],
      recommended_vc_m_min: null,
      recommended_feed_mm_rev: null,
      recommended_ap_mm: null,
      predicted_mrr_cm3_min: null,
      predicted_motor_power_kw: null,
      predicted_ra_um: null,
      predicted_tool_life_minutes: null,
      optimization_status: "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED",
    }],
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: infeasible }));
  assert.match(html, /RESTRIÇÕES INCOMPATÍVEIS — SEM RECOMENDAÇÃO/);
  assert.match(html, /OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED/);
  assert.doesNotMatch(html, /<button/i);
  assert.doesNotMatch(html, /sobrescrever|enviar à máquina/i);
});

test("renders the operational risk panel, category scores, mitigations, and governance", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Matriz de risco operacional/);
  assert.match(html, /RISCO BAIXO/);
  assert.match(html, /Score consolidado/);
  assert.match(html, /0\.0 \/ 100/);
  assert.match(html, /Risco Dimensional/);
  assert.match(html, /Risco Dinâmico/);
  assert.match(html, /Risco Energético/);
  assert.match(html, /Risco Desgaste/);
  assert.match(html, /Recomendações analíticas de mitigação/);
  assert.match(html, /Manter revisão humana e homologação de processo/);
  assert.match(html, /MATRIZ DE RISCO ANALÍTICA CONSOLIDADA - AVALIAÇÃO PRELIMINAR DE PROCESSO SEM VALIDADE DE LAUDO PERICIAL/);
  assert.doesNotMatch(html, /<button/i);
});

test("renders the chronological process sheet, clamping metadata, and governance note", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Folha de processo operacional/);
  assert.match(html, /Peça cad-report-001 · Revisão ANALYTICAL-1/);
  assert.match(html, /2 operações · 17\.083 min/);
  assert.match(html, /Diâmetro do bruto/);
  assert.match(html, /52\.000 mm/);
  assert.match(html, /Comprimento do bruto/);
  assert.match(html, /101\.000 mm/);
  assert.match(html, /CONFIRM_CHUCK_CONTACT_AND_STOCK_PROJECTION_MANUALLY_BEFORE_PROCESS_APPROVAL/);
  assert.match(html, /MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED/);
  assert.match(html, /OP010/);
  assert.match(html, /SETUP/);
  assert.match(html, /OP020/);
  assert.match(html, /ROUGH_TURNING/);
  assert.match(html, /T0101 · ROUGHING TOOL · INSERT_R0\.800_RIGHT_HAND/);
  assert.match(html, /Vc 180\.000 m\/min · f 0\.200 mm\/rot · ap 2\.000 mm · 1500\.0 rpm/);
  assert.match(html, /FOLHA DE PROCESSO TEÓRICA ANALÍTICA - DOCUMENTO ORIENTATIVO SUJEITO À APROVAÇÃO DO PREPARADOR DE MÁQUINAS/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders compliant residual-stock telemetry and physical CMM limitation", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Integridade do sobremetal residual/);
  assert.match(html, /SOBREMETAL HOMOGÊNEO/);
  assert.match(html, /Sobremetal máximo/);
  assert.match(html, /Sobremetal mínimo/);
  assert.match(html, /UNIFORM_ALLOWANCE_COMPLIANT/);
  assert.match(html, /AUDITORIA ANALÍTICA DE MATERIAL REMANESCENTE - NÃO SUBSTITUI MEDIÇÃO TRIDIMENSIONAL FÍSICA EM CMM/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders critical gouging as a red alert without operational controls", () => {
  const gougingReport: MachiningTechnicalReportPayload = {
    ...report,
    residual_stock_audit: {
      ...report.residual_stock_audit,
      sections: [{
        ...report.residual_stock_audit.sections[0],
        in_process_radius_mm: 25.49,
        residual_stock_mm: -0.01,
      }],
      max_residual_stock_mm: -0.01,
      min_residual_stock_mm: -0.01,
      average_stock_allowance_mm: -0.01,
      gouging_detected: true,
      status: "CRITICAL_GOUGING_VIOLATION",
    },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: gougingReport }));
  assert.match(html, /role="alert"[^>]*>ALERTA: SUBCORTE DETECTADO \(GOUGING\)/);
  assert.match(html, /CRITICAL_GOUGING_VIOLATION/);
  assert.match(html, /-0\.010 mm/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders compliant part-deflection telemetry and unsupported-overhang note", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Rigidez elástica da peça/);
  assert.match(html, /2\.810 µm/);
  assert.match(html, /203061\.24 N\/mm/);
  assert.match(html, /RIGIDEZ DA PEÇA CONFORME/);
  assert.match(html, /ESTIMATIVA ANALÍTICA DE FLEXÃO ELÁSTICA DA PEÇA - NÃO CONSIDERA CONTAPONTO OU LUNETA DE APOIO/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders excessive part-deflection warning without physical controls", () => {
  const warningReport: MachiningTechnicalReportPayload = {
    ...report,
    part_elastic_deflection_audit: {
      ...report.part_elastic_deflection_audit,
      max_deflection_um: 25,
      deflection_status: "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING",
    },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: warningReport }));
  assert.match(html, /role="alert"[^>]*>ALERTA: DEFLEXÃO EXCESSIVA DA PEÇA/);
  assert.match(html, /25\.000 µm/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders spindle envelope telemetry, reserve margin, and mandatory note", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Envelope de potência e torque do fuso/);
  assert.match(html, /1500\.0 rpm/);
  assert.match(html, /21\.796 N\.m/);
  assert.match(html, /47\.746 N\.m/);
  assert.match(html, /3\.424 kW/);
  assert.match(html, /7\.500 kW/);
  assert.match(html, /54\.35%/);
  assert.match(html, /ENVELOPE DO FUSO CONFORME/);
  assert.match(html, /ESTIMATIVA ANALÍTICA DE POTÊNCIA E TORQUE DO FUSO - NÃO CONSIDERA DERATING TÉRMICO CONTÍNUO S1\/S6 OU PERDAS POR ENVELHECIMENTO/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders spindle overload warning without physical controls", () => {
  const warningReport: MachiningTechnicalReportPayload = {
    ...report,
    spindle_power_torque_envelope_audit: {
      ...report.spindle_power_torque_envelope_audit,
      operating_points: [{
        ...report.spindle_power_torque_envelope_audit.operating_points[0],
        available_power_kw: 2,
        available_torque_nm: 12.732395447,
        power_margin_kw: -1.42375,
        power_margin_percent: -71.1875,
        torque_margin_nm: -9.063647657,
        status: "POWER_TORQUE_ENVELOPE_EXCEEDED",
      }],
      audit_status: "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING",
    },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: warningReport }));
  assert.match(html, /role="alert"[^>]*>ALERTA: SOBRECARGA DE TORQUE\/POTÊNCIA/);
  assert.match(html, /-71\.19%/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders thermal telemetry and tolerated badge", () => {
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report }));
  assert.match(html, /Expansão térmica e impacto dimensional/);
  assert.match(html, /40\.0 °C/);
  assert.match(html, /35\.0 °C/);
  assert.match(html, /51\.240 µm/);
  assert.match(html, /6\.240 µm/);
  assert.match(html, /51\.24% da menor tolerância declarada/);
  assert.match(html, /DERIVA TÉRMICA TOLERADA/);
  assert.match(html, /ESTIMATIVA ANALÍTICA DE EXPANSÃO TÉRMICA - NÃO CONSIDERA GRADIENTES TÉRMICOS LOCAIS TRANSITÓRIOS OU COMPENSAÇÃO ATIVA POR REFRIGERAÇÃO INTERNA/);
});

test("renders thermal tolerance warning without physical controls", () => {
  const warningReport: MachiningTechnicalReportPayload = {
    ...report,
    thermal_expansion_drift_audit: {
      ...report.thermal_expansion_drift_audit,
      z_axis_tolerance_um: 50,
      audit_status: "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING",
    },
  };
  const html = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: warningReport }));
  assert.match(html, /role="alert"[^>]*>ALERTA: DERIVA TÉRMICA EXCEDE TOLERÂNCIA/);
  assert.doesNotMatch(html, /<button|cycle start|machine send|enviar à máquina/i);
});

test("renders high and critical consolidated risk badges without operational controls", () => {
  const highRisk: MachiningTechnicalReportPayload = {
    ...report,
    risk_matrix: {
      ...report.risk_matrix,
      overall_risk_score: 48.75,
      risk_level: "HIGH_RISK_REQUIRES_MITIGATION",
      dynamic_risk_score: 75,
      energy_risk_score: 75,
      tool_wear_risk_score: 75,
      mitigation_recommendations: ["Revisar os fatores analíticos antes da homologação."],
    },
  };
  const criticalRisk: MachiningTechnicalReportPayload = {
    ...report,
    risk_matrix: {
      ...report.risk_matrix,
      overall_risk_score: 35,
      risk_level: "CRITICAL_INTERVENTION_MANDATORY",
      dimensional_risk_score: 100,
      mitigation_recommendations: ["Interromper a avaliação do processo."],
    },
  };
  const highHtml = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: highRisk }));
  const criticalHtml = renderToStaticMarkup(createElement(MachiningTechnicalReportViewer, { report: criticalRisk }));
  assert.match(highHtml, /ALTO RISCO — MITIGAÇÃO OBRIGATÓRIA/);
  assert.match(highHtml, /aria-label="Risco Dinâmico"[^>]*aria-valuenow="75"/);
  assert.match(criticalHtml, /INTERVENÇÃO CRÍTICA OBRIGATÓRIA/);
  assert.match(criticalHtml, /aria-label="Risco Dimensional"[^>]*aria-valuenow="100"/);
  assert.doesNotMatch(highHtml + criticalHtml, /<button|autorizar|cycle start/i);
});
