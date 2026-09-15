export type CNCControllerProfile = "FANUC_0I" | "SIEMENS_840D" | "HAAS" | "SIMULATED_STUB";
export type TurningOperation = "FACING" | "ROUGH_TURNING" | "FINISHING" | "GROOVING";

export interface MachiningReportSafetyFlags {
  physical_use_authorized: false;
  g9: "PENDING_AUTHORITATIVE_REVIEW";
  no_human_review_bypass: true;
  machine_send: false;
  dnc: false;
  nc_transfer: false;
  cycle_start: false;
  emission_status: "CONTROLLER_PROFILE_UNRESOLVED";
  executable_output: false;
}

export interface MachiningReportToolBreakdown {
  tool: string;
  cutting_time_seconds: number;
  rapid_time_seconds: number;
  cutting_distance_mm: number;
  rapid_distance_mm: number;
}

export interface MachiningCycleTimeEstimate {
  total_cutting_time_seconds: number;
  total_rapid_time_seconds: number;
  total_cycle_time_seconds: number;
  total_cutting_distance_mm: number;
  total_rapid_distance_mm: number;
  rapid_feed_rate_mm_min: number;
  per_tool_breakdown: readonly MachiningReportToolBreakdown[];
  disclaimer: "THEORETICAL_ANALYTICAL_ESTIMATE_NOT_PHYSICALLY_APPROVED";
}

export interface MachiningTechnicalReportPayload {
  schema_version: "vena-ia.cnc-machining-report/v1";
  status: "REQUIRES_HUMAN_REVIEW";
  plan_id: string;
  source_plan_name: null;
  cad_job_id: string;
  controller_profile: CNCControllerProfile;
  program_number: number;
  program_sha256: string;
  analytical_snapshot_at: string;
  tools: readonly {
    tool_id: string;
    operations: readonly TurningOperation[];
  }[];
  cycle_time_estimate: MachiningCycleTimeEstimate;
  total_distance_mm: number;
  envelope_audit: "PASS_DECLARED_2D_ENVELOPE_ONLY";
  machine_envelope: {
    x_min_mm: number;
    x_max_mm: number;
    z_min_mm: number;
    z_max_mm: number;
    chuck_exclusion_zone: {
      x_min_mm: number;
      x_max_mm: number;
      z_min_mm: number;
      z_max_mm: number;
    };
  };
  chuck_proximity: {
    minimum_clearance_mm: number;
    threshold_mm: number;
    closest_segment_index: number;
    warning_code: "WARNING_PROXIMITY_CHUCK" | null;
  };
  geometry_audit: {
    schema_version: "vena-ia.cnc-geometry-dimensional-audit/v1";
    status: "PASS" | "REJECTED";
    deviations: readonly {
      axis: "MAX_RADIUS" | "MIN_Z" | "MAX_Z";
      nominal_mm: number;
      programmed_mm: number;
      signed_deviation_mm: number;
      tolerance_mm: number;
      within_tolerance: boolean;
    }[];
    findings: readonly string[];
    manifest_generation_allowed: boolean;
  };
  surface_roughness_audit: {
    schema_version: "vena-ia.cnc-surface-roughness-audit/v1";
    ra_theoretical_um: number;
    rz_theoretical_um: number;
    finish_feed_mm_per_rev: number;
    insert_nose_radius_mm: number;
    nominal_ra_max_um: number | null;
    compliance_tag: "WITHIN_NOMINAL_RA_TOLERANCE" | "EXCEEDS_NOMINAL_RA_TOLERANCE" | "NOMINAL_RA_TOLERANCE_UNAVAILABLE";
    model_limitation: "IDEAL_KINEMATIC_MODEL_EXCLUDES_VIBRATION_TOOL_WEAR_AND_MATERIAL_EFFECTS";
    safety_flags: MachiningReportSafetyFlags;
  };
  power_force_audit: {
    schema_version: "vena-ia.cnc-machining-power-force-audit/v1";
    material_profile: "AISI_1020" | "ABNT_1045" | "ALUMINUM_6061_T6";
    kc1_1_n_per_mm2: number;
    kienzle_exponent_mc: number;
    feed_mm_per_rev: number;
    depth_of_cut_mm: number;
    cutting_edge_angle_deg: number;
    chip_thickness_mm: number;
    chip_width_mm: number;
    cutting_speed_m_per_min: number;
    spindle_rpm_reference: number;
    max_spindle_rpm: number;
    fc_nominal_n: number;
    pc_cutting_kw: number;
    p_motor_est_kw: number;
    mrr_cm3_min: number;
    machine_power_limit_kw: number;
    power_status: "POWER_WITHIN_LIMITS" | "POWER_EXCEEDED_WARNING";
    spindle_efficiency: 0.8;
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "KIENZLE_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_DYNAMIC_EFFICIENCY";
    safety_flags: MachiningReportSafetyFlags;
  };
  tool_life_audits: readonly {
    schema_version: "vena-ia.cnc-tool-life-taylor-audit/v1";
    tool_id: string;
    tool_material_pair: "CARBIDE_P20_P30_CARBON_STEEL" | "CARBIDE_K10_ALUMINUM_6061_T6";
    cutting_speed_vc_m_per_min: number;
    taylor_n: number;
    taylor_c: number;
    effective_cutting_time_minutes: number;
    estimated_tool_life_minutes: number;
    tool_life_consumed_percent: number;
    integrity_status: "TOOL_LIFE_SAFE" | "TOOL_LIFE_EXHAUSTED_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "TAYLOR_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_THERMAL_AND_LUBRICATION_VARIATION";
    safety_flags: MachiningReportSafetyFlags;
  }[];
  tool_wear_geometry_audits: readonly {
    schema_version: "vena-ia.cnc-tool-wear-geometry-audit/v2";
    source_tool_life_audit: MachiningTechnicalReportPayload["tool_life_audits"][number];
    nominal_nose_radius_mm: number;
    clearance_angle_deg: number;
    position_angle_deg: number;
    maximum_allowable_flank_wear_vb_mm: number;
    estimated_flank_wear_vb_mm: number;
    flank_wear_progress_percent: number;
    effective_nose_radius_mm: number;
    predicted_radial_deviation_um: number;
    predicted_axial_deviation_um: number;
    geometry_tolerance_um: number;
    audit_status: "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE" | "TOOL_WEAR_EXCEEDS_TOLERANCE_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    compensation_authorized: false;
    model_limitation: "ANALYTICAL_TOOL_WEAR_GEOMETRY_DOES_NOT_AUTHORIZE_AUTOMATIC_OFFSET_COMPENSATION";
    safety_flags: MachiningReportSafetyFlags;
  }[];
  cost_time_audit: {
    schema_version: "vena-ia.cnc-machining-cost-time-audit/v1";
    cost_profile: "BRL_STANDARD" | "USD_STANDARD";
    total_cycle_time_minutes: number;
    cutting_time_minutes: number;
    rapid_time_minutes: number;
    tool_change_count: number;
    tool_change_time_minutes_each: number;
    tool_change_time_minutes: number;
    setup_count: number;
    nominal_setup_time_minutes_each: number;
    nominal_setup_time_minutes: number;
    estimated_total_cost: number;
    machine_cost_component: number;
    tooling_wear_cost_component: number;
    machine_hourly_rate: number;
    cutting_edge_cost: number;
    currency: "BRL" | "USD";
    per_tool_wear_costs: readonly {
      tool_id: string;
      effective_cutting_time_minutes: number;
      estimated_tool_life_minutes: number;
      consumed_fraction: number;
      cutting_edge_cost: number;
      estimated_wear_cost: number;
    }[];
    is_theoretical_estimate: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_COST_TIME_EXCLUDES_LOGISTICS_UNPLANNED_DOWNTIME_AND_TAXES";
    safety_flags: MachiningReportSafetyFlags;
  };
  sustainability_audit: {
    schema_version: "vena-ia.cnc-machining-sustainability-audit/v1";
    electrical_energy_kwh: number;
    cutting_energy_kwh: number;
    standby_energy_kwh: number;
    carbon_emission_kg_co2e: number;
    grid_region: "BRASIL_SIN" | "USA_AVG" | "EU_AVG";
    grid_emission_factor_kg_co2e_per_kwh: number;
    motor_power_kw: number;
    standby_power_kw: number;
    cutting_time_minutes: number;
    total_cycle_time_minutes: number;
    electrical_efficiency: number;
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_ENERGY_CARBON_EXCLUDES_EXTERNAL_COOLING_AND_STARTUP_PEAKS";
    safety_flags: MachiningReportSafetyFlags;
  };
  stability_audits: readonly {
    schema_version: "vena-ia.cnc-machining-stability-audit/v1";
    tool_id: string;
    tool_overhang_mm: number;
    tool_diameter_mm: number;
    overhang_ratio_l_d: number;
    young_modulus_mpa: number;
    second_moment_area_mm4: number;
    equivalent_stiffness_n_per_mm: number;
    cutting_force_n: number;
    static_deflection_um: number;
    specific_cutting_pressure_n_per_mm2: number;
    frf_real_compliance_mm_per_n: number;
    depth_of_cut_mm: number;
    stability_limit_depth_mm: number;
    stability_status: "DYNAMICALLY_STABLE" | "CHATTER_HIGH_RISK_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_STABILITY_EXCLUDES_WORKPIECE_AND_SPINDLE_VIBRATION_MODES";
    safety_flags: MachiningReportSafetyFlags;
  }[];
  parameter_optimizations: readonly {
    schema_version: "vena-ia.cnc-machining-parameter-optimization/v1";
    tool_id: string;
    material_profile: "AISI_1020" | "ABNT_1045" | "ALUMINUM_6061_T6";
    programmed_vc_m_min: number;
    programmed_feed_mm_rev: number;
    programmed_ap_mm: number;
    vc_min_m_min: number;
    vc_max_m_min: number;
    feed_min_mm_rev: number;
    feed_max_mm_rev: number;
    ap_min_mm: number;
    ap_max_mm: number;
    target_ra_um: number;
    insert_nose_radius_mm: number;
    cutting_edge_angle_deg: number;
    machine_power_limit_kw: number;
    stability_limit_depth_mm: number;
    overhang_ratio_l_d: number;
    recommended_vc_m_min: number | null;
    recommended_feed_mm_rev: number | null;
    recommended_ap_mm: number | null;
    predicted_mrr_cm3_min: number | null;
    predicted_motor_power_kw: number | null;
    predicted_ra_um: number | null;
    predicted_tool_life_minutes: number | null;
    optimization_status: "OPTIMAL_TRADE_OFF_FOUND" | "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_CUTTING_PARAMETERS_REQUIRE_MANUAL_PROCESS_ENGINEERING_APPROVAL";
    safety_flags: MachiningReportSafetyFlags;
  }[];
  risk_matrix: {
    schema_version: "vena-ia.cnc-machining-risk-matrix/v1";
    envelope_audit: "PASS_DECLARED_2D_ENVELOPE_ONLY" | "ENVELOPE_VIOLATION_DETECTED";
    geometry_audit_status: "PASS" | "REJECTED";
    geometry_manifest_generation_allowed: boolean;
    minimum_chuck_clearance_mm: number;
    chuck_proximity_threshold_mm: number;
    chuck_proximity_warning: boolean;
    max_overhang_ratio_l_d: number;
    dynamic_warning_present: boolean;
    required_motor_power_kw: number;
    machine_power_limit_kw: number;
    power_warning_present: boolean;
    max_tool_life_consumed_percent: number;
    tool_wear_warning_present: boolean;
    overall_risk_score: number;
    risk_level: "LOW_RISK" | "MODERATE_RISK" | "HIGH_RISK_REQUIRES_MITIGATION" | "CRITICAL_INTERVENTION_MANDATORY";
    dimensional_risk_score: number;
    dynamic_risk_score: number;
    energy_risk_score: number;
    tool_wear_risk_score: number;
    mitigation_recommendations: readonly string[];
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "CONSOLIDATED_ANALYTICAL_RISK_MATRIX_IS_PRELIMINARY_AND_NOT_AN_EXPERT_REPORT";
    safety_flags: MachiningReportSafetyFlags;
  };
  process_sheet: {
    schema_version: "vena-ia.cnc-machining-process-sheet/v1";
    part_id: string;
    revision: string;
    source_plan_id: string;
    source_cam_plan: {
      status: "PLANNED_REQUIRES_REVIEW";
      operation_type: TurningOperation;
      passes: readonly {
        sequence: number;
        operation_type: TurningOperation;
        coordinates_rz_mm: readonly { r_mm: number; z_mm: number }[];
        estimated_removed_volume_mm3: number;
      }[];
      material_removal_volume_mm3: number;
      warnings: readonly string[];
      executable_output: false;
      physical_use_authorized: false;
      g9_status: "PENDING_AUTHORITATIVE_REVIEW";
      emission_status: "CONTROLLER_PROFILE_UNRESOLVED";
    };
    source_stock: { diameter_mm: number; z_min_mm: number; z_max_mm: number };
    source_machine_envelope: MachiningTechnicalReportPayload["machine_envelope"];
    source_chuck_proximity: MachiningTechnicalReportPayload["chuck_proximity"];
    source_cycle_time_estimate: MachiningCycleTimeEstimate;
    raw_stock_dimensions: {
      diameter_mm: number;
      axial_length_mm: number;
      z_min_mm: number;
      z_max_mm: number;
    };
    clamping_setup: {
      setup_type: "DECLARED_CHUCK_ENVELOPE_REQUIRES_MANUAL_SETUP";
      chuck_exclusion_zone: MachiningTechnicalReportPayload["machine_envelope"]["chuck_exclusion_zone"];
      minimum_clearance_mm: number;
      proximity_threshold_mm: number;
      estimated_setup_time_min: number;
      clamping_instruction: "CONFIRM_CHUCK_CONTACT_AND_STOCK_PROJECTION_MANUALLY_BEFORE_PROCESS_APPROVAL";
      balance_requirement: "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED";
    };
    sequence_operations: readonly {
      sequence: number;
      operation_id: string;
      phase: "SETUP" | TurningOperation;
      source_pass_sequence: number | null;
      tool_id: string | null;
      tool_description: string | null;
      insert_reference: string | null;
      cutting_speed_vc_m_per_min: number | null;
      feed_mm_per_rev: number | null;
      depth_of_cut_ap_mm: number | null;
      spindle_rpm: number | null;
      feed_rate_mm_min: number | null;
      estimated_time_min: number;
      fixture_requirement: "USE_DECLARED_CHUCK_ENVELOPE_AND_VERIFY_CLEARANCE_MANUALLY";
      balance_requirement: "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED";
    }[];
    total_operations_count: number;
    estimated_total_time_min: number;
    safety_instructions: readonly string[];
    is_theoretical_sheet: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_PROCESS_SHEET_REQUIRES_MACHINE_SETUP_APPROVAL";
    safety_flags: MachiningReportSafetyFlags;
  };
  residual_stock_audit: {
    schema_version: "vena-ia.cnc-residual-stock-audit/v1";
    source_plan_id: string;
    source_cam_plan: MachiningTechnicalReportPayload["process_sheet"]["source_cam_plan"];
    source_nominal_profile: readonly { r_mm: number; z_mm: number }[];
    stock_radius_mm: number;
    finish_allowance_nominal_mm: number;
    linear_tolerance_mm: number;
    tool_cutting_edge_length_mm: number;
    sections: readonly {
      front_z_mm: number;
      rear_z_mm: number;
      nominal_radius_mm: number;
      in_process_radius_mm: number;
      residual_stock_mm: number;
    }[];
    max_residual_stock_mm: number;
    min_residual_stock_mm: number;
    average_stock_allowance_mm: number;
    gouging_detected: boolean;
    status: "UNIFORM_ALLOWANCE_COMPLIANT" | "EXCESS_MATERIAL_DETECTED" | "CRITICAL_GOUGING_VIOLATION";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_RESIDUAL_STOCK_AUDIT_DOES_NOT_REPLACE_PHYSICAL_CMM_MEASUREMENT";
    safety_flags: MachiningReportSafetyFlags;
  };
  part_elastic_deflection_audit: {
    schema_version: "vena-ia.cnc-part-elastic-deflection-audit/v1";
    part_unsupported_length_mm: number;
    minimum_diameter_mm: number;
    radial_cutting_force_n: number;
    young_modulus_mpa: number;
    second_moment_area_mm4: number;
    calculated_stiffness_n_per_mm: number;
    radial_tolerance_mm: number;
    max_deflection_um: number;
    deflection_status: "ELASTIC_DEFLECTION_COMPLIANT" | "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING";
    theoretical: true;
    physical: false;
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_PART_DEFLECTION_EXCLUDES_TAILSTOCK_AND_STEADY_REST_SUPPORT";
    safety_flags: MachiningReportSafetyFlags;
  };
  spindle_power_torque_envelope_audit: {
    schema_version: "vena-ia.cnc-spindle-power-torque-envelope-audit/v2";
    source_power_force_audit?: MachiningTechnicalReportPayload["power_force_audit"];
    spindle_rpm_min: number;
    spindle_rpm_max: number;
    curve_points: readonly {
      spindle_rpm: number;
      available_torque_nm: number;
      available_power_kw: number;
    }[];
    operating_points: readonly {
      spindle_rpm: number;
      required_cutting_power_kw: number;
      required_torque_nm: number;
      available_power_kw: number;
      available_torque_nm: number;
      power_margin_kw: number;
      power_margin_percent: number;
      torque_margin_nm: number;
      status: "WITHIN_POWER_TORQUE_ENVELOPE" | "POWER_TORQUE_ENVELOPE_EXCEEDED";
    }[];
    audit_status: "POWER_TORQUE_ENVELOPE_COMPLIANT" | "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "DECLARED_SPINDLE_POWER_TORQUE_CURVE_REQUIRES_MACHINE_PROFILE_VALIDATION";
    safety_flags: MachiningReportSafetyFlags;
  };
  thermal_expansion_drift_audit: {
    schema_version: "vena-ia.cnc-thermal-expansion-drift-audit/v2";
    material_profile: "AISI_1020" | "ABNT_1045" | "ALUMINUM_6061_T6";
    linear_expansion_coefficient_per_c: number;
    spindle_expansion_coefficient_per_c: number;
    reference_temperature_c: number;
    workpiece_mean_temperature_c: number;
    spindle_mean_temperature_c: number;
    workpiece_mean_temperature_rise_c: number;
    spindle_mean_temperature_rise_c: number;
    workpiece_axial_reference_length_mm: number;
    workpiece_diameter_reference_mm: number;
    spindle_z_reference_length_mm: number;
    workpiece_z_expansion_um: number;
    workpiece_x_expansion_um: number;
    spindle_z_drift_um: number;
    total_z_axis_drift_um: number;
    total_x_axis_drift_um: number;
    z_axis_tolerance_um: number;
    x_axis_tolerance_um: number;
    audit_status: "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE" | "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING";
    theoretical: true;
    physical: false;
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ANALYTICAL_THERMAL_DRIFT_EXCLUDES_TRANSIENT_GRADIENTS_COOLANT_AND_MACHINE_COMPENSATION";
    safety_flags: MachiningReportSafetyFlags;
  };
  chip_breaking_machinability_audit: {
    schema_version: "vena-ia.cnc-chip-breaking-machinability-audit/v2";
    material_profile: "AISI_1020" | "ABNT_1045" | "ALUMINUM_6061_T6";
    chipbreaker_family: "PM" | "PR" | "PF";
    chipbreaker_reference: string;
    feed_mm_per_rev: number;
    depth_of_cut_mm: number;
    insert_nose_radius_mm: number;
    cutting_edge_angle_deg: number;
    rake_angle_deg: number;
    uncut_chip_thickness_mm: number;
    chip_width_mm: number;
    formed_chip_thickness_mm: number;
    chip_compression_ratio: number;
    free_chip_length_mm: number;
    safe_breaking_envelopes: readonly {
      chipbreaker_reference: string;
      feed_min_mm_per_rev: number;
      feed_max_mm_per_rev: number;
      depth_of_cut_min_mm: number;
      depth_of_cut_max_mm: number;
    }[];
    audit_status:
      | "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"
      | "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    automatic_parameter_change_authorized: false;
    model_limitation: "TABULATED_CHIP_BREAKING_ENVELOPE_REQUIRES_PHYSICAL_PROCESS_VALIDATION";
    safety_flags: MachiningReportSafetyFlags;
  };
  coolant_pressure_flow_audit: {
    schema_version: "vena-ia.cnc-coolant-pressure-flow-audit/v2";
    coolant_mode: "FLOOD" | "MQL";
    programmed_flow_l_per_min: number;
    programmed_pressure_bar: number;
    zone_requirements: readonly {
      cutting_zone:
        | "PRIMARY_SHEAR_ZONE"
        | "SECONDARY_TOOL_CHIP_INTERFACE"
        | "TERTIARY_TOOL_WORKPIECE_INTERFACE";
      minimum_flow_l_per_min: number;
      minimum_pressure_bar: number;
    }[];
    minimum_required_flow_l_per_min: number;
    minimum_required_pressure_bar: number;
    flow_margin_percent: number;
    pressure_margin_percent: number;
    thermal_dissipation_status:
      | "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS"
      | "INSUFFICIENT_THERMAL_DISSIPATION_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    automatic_coolant_control_authorized: false;
    model_limitation: "TABULATED_COOLANT_DEMAND_REQUIRES_MACHINE_AND_NOZZLE_PHYSICAL_VALIDATION";
    safety_flags: MachiningReportSafetyFlags;
  };
  workholding_clamping_audit: {
    schema_version: "vena-ia.cnc-workholding-clamping-audit/v1";
    static_clamping_force_per_jaw_n: number;
    jaw_mass_kg: number;
    center_of_mass_radius_mm: number;
    operating_rpm: number;
    maximum_declared_rpm: number;
    axial_cutting_force_n: number;
    friction_coefficient: number;
    required_safety_factor: number;
    centrifugal_force_per_jaw_n: number;
    total_centrifugal_loss_n: number;
    dynamic_clamping_force_total_n: number;
    friction_resistance_n: number;
    clamping_safety_factor: number;
    clamping_status:
      | "DYNAMIC_CLAMPING_SAFE"
      | "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    automatic_chuck_control_authorized: false;
    model_limitation: "ANALYTICAL_CLAMPING_ESTIMATE_REQUIRES_PHYSICAL_CHUCK_LOAD_MEASUREMENT";
    safety_flags: MachiningReportSafetyFlags;
  };
  tailstock_thrust_audit: {
    schema_version: "vena-ia.cnc-tailstock-thrust-audit/v1";
    tailstock_force_n: number;
    critical_buckling_load_n: number;
    max_supported_deflection_um: number;
    engagement_z_coordinate_mm: number;
    total_supported_length_mm: number;
    minimum_diameter_mm: number;
    cutting_load_position_mm: number;
    radial_cutting_force_n: number;
    young_modulus_mpa: number;
    second_moment_area_mm4: number;
    effective_length_factor: number;
    warning_threshold_n: number;
    tailstock_status:
      | "TAILSTOCK_SUPPORT_COMPLIANT"
      | "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    automatic_tailstock_control_authorized: false;
    model_limitation: "ANALYTICAL_TAILSTOCK_SUPPORT_EXCLUDES_CENTER_ECCENTRICITY_AND_QUILL_BEARING_WEAR";
    safety_flags: MachiningReportSafetyFlags;
  };
  spindle_harmonic_dynamics_audit: {
    schema_version: "vena-ia.cnc-spindle-harmonic-dynamics-audit/v1";
    system_stiffness_n_per_m: number;
    effective_mass_kg: number;
    workpiece_mass_kg: number;
    mass_eccentricity_mm: number;
    natural_angular_frequency_rad_s: number;
    first_critical_rpm: number;
    operating_rpm: number;
    resonance_proximity_percent: number;
    resonance_exclusion_percent: number;
    unbalance_force_n: number;
    bearing_admissible_force_n: number;
    dynamic_status:
      | "SPINDLE_DYNAMICS_COMPLIANT"
      | "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING"
      | "DYNAMIC_UNBALANCE_EXCESSIVE_FORCE_WARNING";
    is_theoretical_model: true;
    physical_use_authorized: false;
    automatic_spindle_control_authorized: false;
    model_limitation: "ANALYTICAL_CRITICAL_SPEED_EXCLUDES_VISCOUS_DAMPING_AND_BEARING_RACE_DEFECTS";
    safety_flags: MachiningReportSafetyFlags;
  };
  jaw_clamping_pressure_audit: {
    schema_version: "vena-ia.cnc-jaw-clamping-pressure-audit/v1";
    source_workholding_clamping_audit: MachiningTechnicalReportPayload["workholding_clamping_audit"];
    material_profile: "AISI_1020" | "ABNT_1045" | "ALUMINUM_6061_T6";
    jaw_count: 3;
    jaw_width_mm: number;
    effective_contact_length_mm: number;
    contact_area_mm2: number;
    dynamic_force_per_jaw_n: number;
    minimum_retention_pressure_mpa: number;
    mean_contact_pressure_mpa: number;
    material_yield_strength_mpa: number;
    pressure_ratio_percent: number;
    clamping_pressure_status:
      | "JAW_SURFACE_INDENTATION_RISK_WARNING"
      | "INSUFFICIENT_CLAMPING_PRESSURE_WARNING"
      | "CLAMPING_PRESSURE_COMPLIANT";
    theoretical: true;
    physical: false;
    is_theoretical_model: true;
    physical_use_authorized: false;
    automatic_chuck_pressure_control_authorized: false;
    model_limitation: "ESTIMATIVA ANALÍTICA DE PRESSÃO DE FIXAÇÃO - NÃO CONSIDERA SERRILHADOS, RAIOS DE CANTO OU DISTRIBUIÇÃO HERTZIANA NÃO LINEAR NAS CASTANHAS";
    safety_flags: MachiningReportSafetyFlags;
  };
  guideway_load_audit: {
    schema_version: "vena-ia.cnc-guideway-load-audit/v1";
    source_power_force_audit: MachiningTechnicalReportPayload["power_force_audit"];
    block_count: 4;
    feed_force_ratio: number;
    radial_force_ratio: number;
    tangential_cutting_force_n: number;
    axial_feed_force_n: number;
    radial_cutting_force_n: number;
    lever_arm_x_mm: number;
    lever_arm_y_mm: number;
    lever_arm_z_mm: number;
    block_spacing_x_mm: number;
    rail_spacing_y_mm: number;
    block_spacing_z_mm: number;
    pitching_moment_nm: number;
    yawing_moment_nm: number;
    rolling_moment_nm: number;
    direct_load_per_block_n: number;
    pitching_reaction_per_block_n: number;
    yawing_reaction_per_block_n: number;
    rolling_reaction_per_block_n: number;
    max_block_load_n: number;
    static_capacity_n: number;
    load_ratio_percent: number;
    guideway_status:
      | "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING"
      | "GUIDEWAY_LOAD_COMPLIANT";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ESTIMATIVA ANALÍTICA DE CARGA NOS GUIAS LINEARES - NÃO CONSIDERA PRÉ-CARGA INTERNA DOS PATINS, ERROS DE GEOMETRIA DO BARRAMENTO OU DESGASTE DE ESFERAS/ROLETES";
    safety_flags: MachiningReportSafetyFlags;
  };
  ballscrew_axial_mechanics_audit: {
    schema_version: "vena-ia.cnc-ballscrew-axial-mechanics-audit/v1";
    source_guideway_load_audit: MachiningTechnicalReportPayload["guideway_load_audit"];
    guide_friction_coefficient: number;
    carriage_mass_kg: number;
    gravitational_acceleration_m_s2: 9.80665;
    carriage_acceleration_m_s2: number;
    ballscrew_root_diameter_mm: number;
    ballscrew_lead_mm_per_rev: number;
    ballscrew_length_mm: number;
    young_modulus_mpa: number;
    buckling_mounting_factor: number;
    critical_speed_mounting_factor: number;
    axial_feed_rate_mm_per_min: number;
    area_moment_of_inertia_mm4: number;
    total_axial_thrust_n: number;
    euler_buckling_limit_n: number;
    critical_speed_rpm: number;
    operating_ballscrew_rpm: number;
    load_ratio_percent: number;
    speed_ratio_percent: number;
    ballscrew_status:
      | "BALLSCREW_AXIAL_BUCKLING_RISK_WARNING"
      | "BALLSCREW_CRITICAL_SPEED_WARNING"
      | "BALLSCREW_MECHANICS_COMPLIANT";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ESTIMATIVA ANALÍTICA DE ESFORÇOS NO FUSO DE ESFERAS - NÃO CONSIDERA PRÉ-CARGA DE CASTANHA DUPLA, ERROS DE PASSO OU FOLGA AXIAL POR DESGASTE";
    safety_flags: MachiningReportSafetyFlags;
  };
  spindle_bearing_thermal_audit: {
    schema_version: "vena-ia.cnc-spindle-bearing-thermal-audit/v1";
    source_guideway_load_audit: MachiningTechnicalReportPayload["guideway_load_audit"];
    internal_preload_n: number;
    combined_equivalent_load_n: number;
    load_friction_factor_f1: number;
    viscous_friction_factor_f0: number;
    bearing_mean_diameter_mm: number;
    lubricant_kinematic_viscosity_mm2_s: number;
    operating_rpm: number;
    convection_coefficient_w_m2_k: number;
    housing_dissipation_area_m2: number;
    ambient_temperature_c: 20;
    max_admissible_temp_c: number;
    load_torque_nm: number;
    viscous_torque_nm: number;
    total_friction_torque_nm: number;
    total_heat_dissipated_w: number;
    steady_state_temperature_rise_c: number;
    estimated_bearing_temp_c: number;
    bearing_status:
      | "SPINDLE_BEARING_OVERHEATING_WARNING"
      | "SPINDLE_BEARING_THERMAL_COMPLIANT";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ESTIMATIVA ANALÍTICA DE CARGA TÉRMICA EM ROLAMENTOS - NÃO SUBSTITUI SENSORES DE TEMPERATURA PT100 OU TERMOGRAFIA FÍSICA DO CABEÇOTE";
    safety_flags: MachiningReportSafetyFlags;
  };
  spindle_bearing_life_audit: {
    schema_version: "vena-ia.cnc-spindle-bearing-life-audit/v1";
    source_spindle_bearing_thermal_audit: MachiningTechnicalReportPayload["spindle_bearing_thermal_audit"];
    bearing_type: "ANGULAR_CONTACT_BALL" | "CYLINDRICAL_ROLLER" | "TAPERED_ROLLER";
    life_exponent_p: number;
    axial_preload_n: number;
    radial_load_n: number;
    axial_load_n: number;
    radial_load_factor_x: number;
    axial_load_factor_y: number;
    equivalent_dynamic_load_n: number;
    dynamic_capacity_c_n: number;
    required_kinematic_viscosity_nu1_mm2_s: number;
    operating_kinematic_viscosity_nu_mm2_s: number;
    viscosity_ratio_kappa: number;
    a_iso_modification_factor: number;
    basic_l10_million_revs: number;
    l10_million_revs: number;
    operating_rpm: number;
    l10h_hours: number;
    minimum_admissible_l10h_hours: number;
    bearing_life_status: "PREMATURE_BEARING_FATIGUE_WARNING" | "BEARING_FATIGUE_LIFE_COMPLIANT";
    is_theoretical_model: true;
    physical_use_authorized: false;
    model_limitation: "ESTIMATIVA ANALÍTICA DE VIDA ÚTIL L10h - NÃO CONSIDERA CONTAMINAÇÃO SÓLIDA DO LUBRIFICANTE, DESALINHAMENTO DE MONTAGEM OU CORROSÃO";
    safety_flags: MachiningReportSafetyFlags;
  };
  coordinate_convention: "LATHE_X_DIAMETER_Z";
  governance_stamp: "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO";
  safety_flags: MachiningReportSafetyFlags;
  limitations: readonly string[];
}

interface MachiningTechnicalReportViewerProps {
  report: MachiningTechnicalReportPayload;
}

function duration(seconds: number): string {
  const safeSeconds = Math.max(0, Math.round(seconds));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const remainingSeconds = safeSeconds % 60;
  return [hours, minutes, remainingSeconds].map((value) => String(value).padStart(2, "0")).join(":");
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-slate-700 bg-slate-950 p-3">
    <dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt>
    <dd className="mt-1 font-mono text-sm text-cyan-100">{value}</dd>
  </div>;
}

export function MachiningTechnicalReportViewer({ report }: MachiningTechnicalReportViewerProps) {
  const estimate = report.cycle_time_estimate;
  const proximityWarning = report.chuck_proximity.warning_code === "WARNING_PROXIMITY_CHUCK";
  const dimensionalPass = report.geometry_audit.status === "PASS";
  const powerWithinLimits = report.power_force_audit.power_status === "POWER_WITHIN_LIMITS";
  const residualCompliant = report.residual_stock_audit.status === "UNIFORM_ALLOWANCE_COMPLIANT";
  const gougingDetected = report.residual_stock_audit.status === "CRITICAL_GOUGING_VIOLATION";
  const partRigidityCompliant = report.part_elastic_deflection_audit.deflection_status === "ELASTIC_DEFLECTION_COMPLIANT";
  const spindleEnvelopeCompliant = report.spindle_power_torque_envelope_audit.audit_status === "POWER_TORQUE_ENVELOPE_COMPLIANT";
  const spindleOperatingPoint = report.spindle_power_torque_envelope_audit.operating_points[0];
  const spindleReserve = Math.min(100, Math.max(0, spindleOperatingPoint.power_margin_percent));
  const thermalDriftTolerated = report.thermal_expansion_drift_audit.audit_status === "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE";
  const thermalImpact = Math.max(
    report.thermal_expansion_drift_audit.total_z_axis_drift_um / report.thermal_expansion_drift_audit.z_axis_tolerance_um,
    report.thermal_expansion_drift_audit.total_x_axis_drift_um / report.thermal_expansion_drift_audit.x_axis_tolerance_um,
  ) * 100;
  const chipBreaking = report.chip_breaking_machinability_audit;
  const chipBreakingSafe = chipBreaking.audit_status === "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE";
  const chipBreakingEnvelope = chipBreaking.safe_breaking_envelopes.find(
    (item) => item.chipbreaker_reference === chipBreaking.chipbreaker_reference,
  )!;
  const chipFeedPosition = Math.min(100, Math.max(
    0,
    ((chipBreaking.feed_mm_per_rev - chipBreakingEnvelope.feed_min_mm_per_rev)
      / (chipBreakingEnvelope.feed_max_mm_per_rev - chipBreakingEnvelope.feed_min_mm_per_rev)) * 100,
  ));
  const chipDepthPosition = Math.min(100, Math.max(
    0,
    ((chipBreaking.depth_of_cut_mm - chipBreakingEnvelope.depth_of_cut_min_mm)
      / (chipBreakingEnvelope.depth_of_cut_max_mm - chipBreakingEnvelope.depth_of_cut_min_mm)) * 100,
  ));
  const coolantAudit = report.coolant_pressure_flow_audit;
  const coolantDemandAdequate = coolantAudit.thermal_dissipation_status === "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS";
  const workholdingAudit = report.workholding_clamping_audit;
  const dynamicClampingSafe = workholdingAudit.clamping_status === "DYNAMIC_CLAMPING_SAFE";
  const tailstockAudit = report.tailstock_thrust_audit;
  const tailstockSupportCompliant = tailstockAudit.tailstock_status === "TAILSTOCK_SUPPORT_COMPLIANT";
  const harmonicAudit = report.spindle_harmonic_dynamics_audit;
  const spindleDynamicsCompliant = harmonicAudit.dynamic_status === "SPINDLE_DYNAMICS_COMPLIANT";
  const spindleDynamicsBadge = spindleDynamicsCompliant
    ? "DINÂMICA DE FUSO ESTÁVEL"
    : harmonicAudit.dynamic_status === "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING"
      ? "ALERTA: PROXIMIDADE DE VELOCIDADE CRÍTICA"
      : "ALERTA: FORÇA DE DESBALANCEAMENTO EXCESSIVA";
  const harmonicMarkerPosition = Math.min(
    100,
    Math.max(0, harmonicAudit.resonance_proximity_percent / 30 * 100),
  );
  const jawPressureAudit = report.jaw_clamping_pressure_audit;
  const jawPressureCompliant = jawPressureAudit.clamping_pressure_status === "CLAMPING_PRESSURE_COMPLIANT";
  const jawPressureBadge = jawPressureCompliant
    ? "PRESSÃO DE CONTATO CONFORME"
    : jawPressureAudit.clamping_pressure_status === "JAW_SURFACE_INDENTATION_RISK_WARNING"
      ? "ALERTA: RISCO DE MARCAS/DEFORMAÇÃO PLÁSTICA"
      : "ALERTA: PRESSÃO DE FIXAÇÃO INSUFICIENTE";
  const guidewayAudit = report.guideway_load_audit;
  const guidewayCompliant = guidewayAudit.guideway_status === "GUIDEWAY_LOAD_COMPLIANT";
  const ballscrewAudit = report.ballscrew_axial_mechanics_audit;
  const ballscrewCompliant = ballscrewAudit.ballscrew_status === "BALLSCREW_MECHANICS_COMPLIANT";
  const spindleBearingAudit = report.spindle_bearing_thermal_audit;
  const spindleBearingCompliant = spindleBearingAudit.bearing_status === "SPINDLE_BEARING_THERMAL_COMPLIANT";
  const bearingLifeAudit = report.spindle_bearing_life_audit;
  const bearingLifeCompliant = bearingLifeAudit.bearing_life_status === "BEARING_FATIGUE_LIFE_COMPLIANT";
  const riskPresentation = {
    LOW_RISK: ["RISCO BAIXO", "border-emerald-500 bg-emerald-950 text-emerald-100"],
    MODERATE_RISK: ["RISCO MODERADO", "border-yellow-500 bg-yellow-950 text-yellow-100"],
    HIGH_RISK_REQUIRES_MITIGATION: ["ALTO RISCO — MITIGAÇÃO OBRIGATÓRIA", "border-orange-500 bg-orange-950 text-orange-100"],
    CRITICAL_INTERVENTION_MANDATORY: ["INTERVENÇÃO CRÍTICA OBRIGATÓRIA", "border-red-500 bg-red-950 text-red-100"],
  }[report.risk_matrix.risk_level];

  return <article className="space-y-6 rounded-2xl border border-slate-700 bg-slate-900 p-6 text-slate-100" aria-label="Relatório técnico CNC">
    <header className="space-y-3">
      <div className="rounded-lg border-2 border-amber-400 bg-amber-950/60 p-4 text-center font-bold text-amber-100" role="alert">
        {report.governance_stamp}
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-cyan-400">{report.schema_version}</p>
        <h1 className="mt-1 text-2xl font-semibold">Relatório técnico de usinagem</h1>
        <p className="mt-1 text-sm text-slate-300">Plano {report.plan_id} · Programa {report.program_number} · {report.controller_profile}</p>
      </div>
    </header>

    <section aria-labelledby="report-cycle-heading" className="space-y-3">
      <h2 id="report-cycle-heading" className="text-lg font-semibold">Estimativa analítica</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Tempo total" value={duration(estimate.total_cycle_time_seconds)} />
        <Metric label="Tempo de corte" value={duration(estimate.total_cutting_time_seconds)} />
        <Metric label="Tempo rápido" value={duration(estimate.total_rapid_time_seconds)} />
        <Metric label="Distância total" value={`${report.total_distance_mm.toFixed(3)} mm`} />
      </dl>
      <p className="text-xs font-semibold text-amber-200">ESTIMATIVA ANALÍTICA TEÓRICA - NÃO REPRESENTA TEMPO FÍSICO HOMOLOGADO</p>
    </section>

    <section aria-labelledby="report-tools-heading" className="space-y-3">
      <h2 id="report-tools-heading" className="text-lg font-semibold">Ferramentas e operações</h2>
      <ul className="grid gap-3 md:grid-cols-2">
        {report.tools.map((tool) => <li key={tool.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-3">
          <span className="font-mono text-cyan-100">{tool.tool_id}</span>
          <span className="ml-2 text-sm text-slate-300">{tool.operations.join(" · ")}</span>
        </li>)}
      </ul>
    </section>

    <section aria-labelledby="report-audit-heading" className="space-y-3">
      <h2 id="report-audit-heading" className="text-lg font-semibold">Auditoria declarada</h2>
      <dl className="grid gap-3 sm:grid-cols-2">
        <Metric label="Envelope 2D" value={report.envelope_audit} />
        <Metric label="Folga mínima da placa" value={`${report.chuck_proximity.minimum_clearance_mm.toFixed(3)} mm`} />
      </dl>
      {proximityWarning ? <p role="alert" className="rounded-lg border border-red-500 bg-red-950/60 p-3 font-mono text-red-100">WARNING_PROXIMITY_CHUCK</p> : null}
      <p className="font-mono text-xs text-slate-400">SHA-256 do programa: {report.program_sha256}</p>
    </section>

    <section aria-labelledby="report-dimensional-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-dimensional-heading" className="text-lg font-semibold">Auditoria geométrica dimensional</h2>
        <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${dimensionalPass ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {dimensionalPass ? "AUDITORIA GEOMÉTRICA CONFORME" : "DESVIO DETECTADO"}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead><tr className="border-b border-slate-700 text-slate-400">
            <th className="p-2">Dimensão</th><th className="p-2">Nominal</th><th className="p-2">Programada</th><th className="p-2">Desvio</th><th className="p-2">Tolerância</th>
          </tr></thead>
          <tbody>{report.geometry_audit.deviations.map((item) => <tr key={item.axis} className="border-b border-slate-800 font-mono">
            <td className="p-2">{item.axis}</td><td className="p-2">{item.nominal_mm.toFixed(3)} mm</td><td className="p-2">{item.programmed_mm.toFixed(3)} mm</td><td className={`p-2 ${item.within_tolerance ? "text-emerald-300" : "text-red-300"}`}>{item.signed_deviation_mm.toFixed(3)} mm</td><td className="p-2">±{item.tolerance_mm.toFixed(3)} mm</td>
          </tr>)}</tbody>
        </table>
      </div>
      <a href={`/api/v1/cnc/turning/plans/${encodeURIComponent(report.plan_id)}/report/download`} download className="inline-flex rounded-lg border border-cyan-500 bg-cyan-950 px-4 py-2 text-sm font-semibold text-cyan-100">
        Exportar laudo textual — {report.governance_stamp}
      </a>
    </section>

    <section aria-labelledby="report-roughness-heading" className="space-y-3">
      <h2 id="report-roughness-heading" className="text-lg font-semibold">Acabamento superficial teórico</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Ra teórico" value={`${report.surface_roughness_audit.ra_theoretical_um.toFixed(3)} µm`} />
        <Metric label="Rz teórico" value={`${report.surface_roughness_audit.rz_theoretical_um.toFixed(3)} µm`} />
        <Metric label="Avanço" value={`${report.surface_roughness_audit.finish_feed_mm_per_rev.toFixed(3)} mm/rot`} />
        <Metric label="Raio de ponta" value={`${report.surface_roughness_audit.insert_nose_radius_mm.toFixed(3)} mm`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">{report.surface_roughness_audit.compliance_tag}</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        RUGOSIDADE TEÓRICA CINEMÁTICA - NÃO CONSIDERA VIBRAÇÃO OU DESGASTE DA FERRAMENTA
      </p>
    </section>

    <section aria-labelledby="report-power-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-power-heading" className="text-lg font-semibold">Telemetria energética teórica</h2>
        <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${powerWithinLimits ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-amber-500 bg-amber-950 text-amber-100"}`}>
          {powerWithinLimits ? "POTÊNCIA ADEQUADA" : "ALERTA DE POTÊNCIA EXCESSIVA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Força tangencial estimada" value={`${report.power_force_audit.fc_nominal_n.toFixed(2)} N`} />
        <Metric label="Potência de corte" value={`${report.power_force_audit.pc_cutting_kw.toFixed(3)} kW`} />
        <Metric label="Potência estimada do motor" value={`${report.power_force_audit.p_motor_est_kw.toFixed(3)} kW`} />
        <Metric label="MRR" value={`${report.power_force_audit.mrr_cm3_min.toFixed(3)} cm³/min`} />
      </dl>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ENERGÉTICA ANALÍTICA DE KIENZLE - NÃO CONSIDERA RENDIMENTO DINÂMICO REAL
      </p>
    </section>

    <section aria-labelledby="report-tool-life-heading" className="space-y-3">
      <h2 id="report-tool-life-heading" className="text-lg font-semibold">Vida útil teórica das ferramentas</h2>
      <ul className="space-y-3">
        {report.tool_life_audits.map((audit) => {
          const safe = audit.integrity_status === "TOOL_LIFE_SAFE";
          const progress = Math.min(100, Math.max(0, audit.tool_life_consumed_percent));
          return <li key={audit.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-cyan-100">{audit.tool_id}</span>
              <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${safe ? "border-emerald-500 text-emerald-100" : "border-red-500 text-red-100"}`}>
                {safe ? "VIDA ÚTIL SEGURA" : "ALERTA: DESGASTE CRÍTICO"}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-300">Vida estimada: {audit.estimated_tool_life_minutes.toFixed(2)} min · Consumo: {audit.tool_life_consumed_percent.toFixed(2)}%</p>
            <div role="progressbar" aria-label={`Consumo de vida útil ${audit.tool_id}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
              <div className={safe ? "h-full bg-emerald-500" : "h-full bg-red-500"} style={{ width: `${progress}%` }} />
            </div>
          </li>;
        })}
      </ul>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE TAYLOR - NÃO CONSIDERA FLUTUAÇÕES TÉRMICAS REAIS OU LUBRIFICAÇÃO
      </p>
    </section>

    <section aria-labelledby="report-tool-wear-heading" className="space-y-3">
      <h2 id="report-tool-wear-heading" className="text-lg font-semibold">Desgaste geométrico estimado</h2>
      <ul className="space-y-3">
        {report.tool_wear_geometry_audits.map((audit) => {
          const acceptable = audit.audit_status === "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE";
          const toleranceImpact = Math.min(100, Math.max(0, audit.predicted_radial_deviation_um / audit.geometry_tolerance_um * 100));
          return <li key={audit.source_tool_life_audit.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-cyan-100">{audit.source_tool_life_audit.tool_id}</span>
              <span role={acceptable ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${acceptable ? "border-emerald-500 text-emerald-100" : "border-red-500 text-red-100"}`}>
                {acceptable ? "DESGASTE GEOMÉTRICO ACEITÁVEL" : "ALERTA: DESVIO POR DESGASTE CRÍTICO"}
              </span>
            </div>
            <dl className="mt-3 grid gap-3 sm:grid-cols-3">
              <Metric label="Desgaste de flanco VB" value={`${audit.estimated_flank_wear_vb_mm.toFixed(4)} mm`} />
              <Metric label="Desvio radial induzido" value={`${audit.predicted_radial_deviation_um.toFixed(3)} µm`} />
              <Metric label="Raio de ponta efetivo" value={`${audit.effective_nose_radius_mm.toFixed(4)} mm`} />
            </dl>
            <div className="mt-3">
              <div className="flex items-center justify-between gap-2 text-sm">
                <span>Desvio induzido vs. tolerância</span>
                <span className="font-mono">{toleranceImpact.toFixed(2)}%</span>
              </div>
              <div role="progressbar" aria-label={`Desvio por desgaste ${audit.source_tool_life_audit.tool_id}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={toleranceImpact} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
                <div className={acceptable ? "h-full bg-emerald-500" : "h-full bg-red-500"} style={{ width: `${toleranceImpact}%` }} />
              </div>
            </div>
          </li>;
        })}
      </ul>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE DESGASTE DE FLANCO - NÃO CONSIDERA LASCAMENTO, DESGASTE DE CRATERA OU COMPENSAÇÃO ATIVA DE CORRETOR CNC
      </p>
    </section>

    <section aria-labelledby="report-cost-time-heading" className="space-y-3">
      <h2 id="report-cost-time-heading" className="text-lg font-semibold">Resumo econômico e de tempo</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Metric label="Tempo total estimado" value={`${report.cost_time_audit.total_cycle_time_minutes.toFixed(2)} min`} />
        <Metric label="Corte efetivo" value={`${report.cost_time_audit.cutting_time_minutes.toFixed(2)} min`} />
        <Metric label="Avanço em vazio" value={`${report.cost_time_audit.rapid_time_minutes.toFixed(2)} min`} />
        <Metric label="Trocas de ferramenta" value={`${report.cost_time_audit.tool_change_time_minutes.toFixed(2)} min`} />
        <Metric label="Setup nominal" value={`${report.cost_time_audit.nominal_setup_time_minutes.toFixed(2)} min`} />
      </dl>
      <dl className="grid gap-3 sm:grid-cols-3">
        <Metric label="Custo de máquina" value={`${report.cost_time_audit.currency} ${report.cost_time_audit.machine_cost_component.toFixed(2)}`} />
        <Metric label="Depreciação de insertos" value={`${report.cost_time_audit.currency} ${report.cost_time_audit.tooling_wear_cost_component.toFixed(2)}`} />
        <Metric label="Custo total estimado" value={`${report.cost_time_audit.currency} ${report.cost_time_audit.estimated_total_cost.toFixed(2)}`} />
      </dl>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ECONÔMICA E DE TEMPO ANALÍTICA - NÃO CONSIDERA FLUTUAÇÕES LOGÍSTICAS, PARADAS NÃO PROGRAMADAS OU IMPOSTOS
      </p>
    </section>

    <section aria-labelledby="report-sustainability-heading" className="space-y-3">
      <h2 id="report-sustainability-heading" className="text-lg font-semibold">Resumo ecológico e energético</h2>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Consumo elétrico previsto" value={`${report.sustainability_audit.electrical_energy_kwh.toFixed(4)} kWh`} />
        <Metric label="Energia de corte" value={`${report.sustainability_audit.cutting_energy_kwh.toFixed(4)} kWh`} />
        <Metric label="Energia em espera" value={`${report.sustainability_audit.standby_energy_kwh.toFixed(4)} kWh`} />
        <Metric label="Pegada de carbono" value={`${report.sustainability_audit.carbon_emission_kg_co2e.toFixed(4)} kg CO2e`} />
      </dl>
      <div aria-label="Matriz energética regional informativa" className="flex flex-wrap gap-2">
        {([
          ["BRASIL_SIN", "Brasil"],
          ["USA_AVG", "EUA"],
          ["EU_AVG", "Europa"],
        ] as const).map(([region, label]) => <span key={region} aria-current={report.sustainability_audit.grid_region === region ? "true" : undefined} className={`rounded-full border px-3 py-1 text-xs ${report.sustainability_audit.grid_region === region ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-slate-600 text-slate-400"}`}>
          {label} · {region}
        </span>)}
      </div>
      <p className="font-mono text-xs text-slate-300">Fator da matriz: {report.sustainability_audit.grid_emission_factor_kg_co2e_per_kwh.toFixed(3)} kg CO2e/kWh</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ECOLÓGICA E ENERGÉTICA ANALÍTICA - NÃO CONSIDERA DINÂMICA AUXILIAR DE REFRIGERAÇÃO EXTERNA OU PICOS DE PARTIDA
      </p>
    </section>

    <section aria-labelledby="report-stability-heading" className="space-y-3">
      <h2 id="report-stability-heading" className="text-lg font-semibold">Rigidez e estabilidade dinâmica</h2>
      <ul className="space-y-3">
        {report.stability_audits.map((audit) => {
          const stable = audit.stability_status === "DYNAMICALLY_STABLE";
          return <li key={audit.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-cyan-100">{audit.tool_id}</span>
              <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${stable ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-amber-500 bg-amber-950 text-amber-100"}`}>
                {stable ? "SISTEMA ESTÁVEL" : "ALERTA: RISCO DE CHATTER (L/D CRÍTICO)"}
              </span>
            </div>
            <dl className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Metric label="Relação de balanço L/D" value={audit.overhang_ratio_l_d.toFixed(2)} />
              <Metric label="Deflexão estática" value={`${audit.static_deflection_um.toFixed(3)} µm`} />
              <Metric label="Rigidez da haste" value={`${audit.equivalent_stiffness_n_per_mm.toFixed(2)} N/mm`} />
              <Metric label="ap limite" value={`${audit.stability_limit_depth_mm.toFixed(3)} mm`} />
            </dl>
          </li>;
        })}
      </ul>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE ESTABILIDADE DINÂMICA - NÃO CONSIDERA MODOS DE VIBRAÇÃO DA PEÇA OU DO FUSO
      </p>
    </section>

    <section aria-labelledby="report-optimization-heading" className="space-y-3">
      <h2 id="report-optimization-heading" className="text-lg font-semibold">Otimização multicritério de parâmetros</h2>
      <ul className="space-y-3">
        {report.parameter_optimizations.map((optimization) => {
          const feasible = optimization.optimization_status === "OPTIMAL_TRADE_OFF_FOUND";
          return <li key={optimization.tool_id} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-cyan-100">{optimization.tool_id}</span>
              <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${feasible ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
                {feasible ? "COMPROMISSO ANALÍTICO ÓTIMO ENCONTRADO" : "RESTRIÇÕES INCOMPATÍVEIS — SEM RECOMENDAÇÃO"}
              </span>
            </div>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm">
                <thead><tr className="border-b border-slate-700 text-slate-400"><th className="p-2">Parâmetro</th><th className="p-2">Programado</th><th className="p-2">Recomendado</th></tr></thead>
                <tbody className="font-mono">
                  <tr className="border-b border-slate-800"><td className="p-2">Vc</td><td className="p-2">{optimization.programmed_vc_m_min.toFixed(3)} m/min</td><td className="p-2">{optimization.recommended_vc_m_min === null ? "—" : `${optimization.recommended_vc_m_min.toFixed(3)} m/min`}</td></tr>
                  <tr className="border-b border-slate-800"><td className="p-2">Avanço f</td><td className="p-2">{optimization.programmed_feed_mm_rev.toFixed(3)} mm/rot</td><td className="p-2">{optimization.recommended_feed_mm_rev === null ? "—" : `${optimization.recommended_feed_mm_rev.toFixed(3)} mm/rot`}</td></tr>
                  <tr className="border-b border-slate-800"><td className="p-2">Profundidade ap</td><td className="p-2">{optimization.programmed_ap_mm.toFixed(3)} mm</td><td className="p-2">{optimization.recommended_ap_mm === null ? "—" : `${optimization.recommended_ap_mm.toFixed(3)} mm`}</td></tr>
                  <tr><td className="p-2">MRR</td><td className="p-2">{report.power_force_audit.mrr_cm3_min.toFixed(3)} cm³/min</td><td className="p-2">{optimization.predicted_mrr_cm3_min === null ? "—" : `${optimization.predicted_mrr_cm3_min.toFixed(3)} cm³/min`}</td></tr>
                </tbody>
              </table>
            </div>
            {!feasible ? <p role="alert" className="mt-3 font-mono text-sm text-red-200">OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED</p> : null}
          </li>;
        })}
      </ul>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        SUGESTÃO ANALÍTICA DE PARÂMETROS DE CORTE - APLICAÇÃO EM MÁQUINA REQUER HOMOLOGAÇÃO MANUAL POR ENGENHARIA DE PROCESSOS
      </p>
    </section>

    <section aria-labelledby="report-risk-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-risk-heading" className="text-lg font-semibold">Matriz de risco operacional</h2>
        <span role="status" className={`rounded-full border px-3 py-1 text-xs font-bold ${riskPresentation[1]}`}>
          {riskPresentation[0]}
        </span>
      </div>
      <Metric label="Score consolidado" value={`${report.risk_matrix.overall_risk_score.toFixed(1)} / 100`} />
      <div aria-label="Painel de risco por categoria" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {([
          ["Dimensional", report.risk_matrix.dimensional_risk_score],
          ["Dinâmico", report.risk_matrix.dynamic_risk_score],
          ["Energético", report.risk_matrix.energy_risk_score],
          ["Desgaste", report.risk_matrix.tool_wear_risk_score],
        ] as const).map(([label, score]) => <div key={label} className="rounded-lg border border-slate-700 bg-slate-950 p-3">
          <div className="flex items-center justify-between gap-2 text-sm"><span>{label}</span><span className="font-mono">{score.toFixed(1)}</span></div>
          <div role="progressbar" aria-label={`Risco ${label}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={score} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
            <div className="h-full bg-orange-500" style={{ width: `${Math.min(100, Math.max(0, score))}%` }} />
          </div>
        </div>)}
      </div>
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
        <h3 className="text-sm font-semibold">Recomendações analíticas de mitigação</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">
          {report.risk_matrix.mitigation_recommendations.map((recommendation) => <li key={recommendation}>{recommendation}</li>)}
        </ul>
      </div>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        MATRIZ DE RISCO ANALÍTICA CONSOLIDADA - AVALIAÇÃO PRELIMINAR DE PROCESSO SEM VALIDADE DE LAUDO PERICIAL
      </p>
    </section>

    <section aria-labelledby="report-process-sheet-heading" className="space-y-3">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 id="report-process-sheet-heading" className="text-lg font-semibold">Folha de processo operacional</h2>
          <p className="text-sm text-slate-300">Peça {report.process_sheet.part_id} · Revisão {report.process_sheet.revision}</p>
        </div>
        <span className="font-mono text-xs text-cyan-200">{report.process_sheet.total_operations_count} operações · {report.process_sheet.estimated_total_time_min.toFixed(3)} min</span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Diâmetro do bruto" value={`${report.process_sheet.raw_stock_dimensions.diameter_mm.toFixed(3)} mm`} />
        <Metric label="Comprimento do bruto" value={`${report.process_sheet.raw_stock_dimensions.axial_length_mm.toFixed(3)} mm`} />
        <Metric label="Folga da placa" value={`${report.process_sheet.clamping_setup.minimum_clearance_mm.toFixed(3)} mm`} />
        <Metric label="Tempo de setup" value={`${report.process_sheet.clamping_setup.estimated_setup_time_min.toFixed(3)} min`} />
      </dl>
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-4 text-sm text-slate-300">
        <p><span className="font-semibold text-slate-100">Fixação:</span> {report.process_sheet.clamping_setup.clamping_instruction}</p>
        <p className="mt-1"><span className="font-semibold text-slate-100">Balanço:</span> {report.process_sheet.clamping_setup.balance_requirement}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm" aria-label="Sequência cronológica de operações CNC">
          <thead><tr className="border-b border-slate-700 text-slate-400">
            <th className="p-2">Seq.</th><th className="p-2">Fase</th><th className="p-2">Ferramenta / inserto</th><th className="p-2">Parâmetros</th><th className="p-2">Tempo</th>
          </tr></thead>
          <tbody>{report.process_sheet.sequence_operations.map((step) => <tr key={step.operation_id} className="border-b border-slate-800 align-top">
            <td className="p-2 font-mono">{step.operation_id}</td>
            <td className="p-2">{step.phase}</td>
            <td className="p-2 font-mono">{step.tool_id === null ? "—" : `${step.tool_id} · ${step.tool_description} · ${step.insert_reference}`}</td>
            <td className="p-2 font-mono">{step.spindle_rpm === null ? "—" : `Vc ${step.cutting_speed_vc_m_per_min?.toFixed(3)} m/min · f ${step.feed_mm_per_rev?.toFixed(3)} mm/rot · ap ${step.depth_of_cut_ap_mm?.toFixed(3)} mm · ${step.spindle_rpm.toFixed(1)} rpm`}</td>
            <td className="p-2 font-mono">{step.estimated_time_min.toFixed(3)} min</td>
          </tr>)}</tbody>
        </table>
      </div>
      <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
        {report.process_sheet.safety_instructions.map((instruction) => <li key={instruction}>{instruction}</li>)}
      </ul>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        FOLHA DE PROCESSO TEÓRICA ANALÍTICA - DOCUMENTO ORIENTATIVO SUJEITO À APROVAÇÃO DO PREPARADOR DE MÁQUINAS
      </p>
    </section>

    <section aria-labelledby="report-residual-stock-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-residual-stock-heading" className="text-lg font-semibold">Integridade do sobremetal residual</h2>
        <span role={gougingDetected ? "alert" : "status"} className={`rounded-full border px-3 py-1 text-xs font-bold ${residualCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : gougingDetected ? "border-red-500 bg-red-950 text-red-100" : "border-amber-500 bg-amber-950 text-amber-100"}`}>
          {residualCompliant ? "SOBREMETAL HOMOGÊNEO" : gougingDetected ? "ALERTA: SUBCORTE DETECTADO (GOUGING)" : "EXCESSO DE MATERIAL DETECTADO"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Sobremetal máximo" value={`${report.residual_stock_audit.max_residual_stock_mm.toFixed(3)} mm`} />
        <Metric label="Sobremetal mínimo" value={`${report.residual_stock_audit.min_residual_stock_mm.toFixed(3)} mm`} />
        <Metric label="Sobremetal médio" value={`${report.residual_stock_audit.average_stock_allowance_mm.toFixed(3)} mm`} />
        <Metric label="Limite analítico" value={`${(report.residual_stock_audit.finish_allowance_nominal_mm + 0.05).toFixed(3)} mm`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">{report.residual_stock_audit.status}</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        AUDITORIA ANALÍTICA DE MATERIAL REMANESCENTE - NÃO SUBSTITUI MEDIÇÃO TRIDIMENSIONAL FÍSICA EM CMM
      </p>
    </section>

    <section aria-labelledby="report-part-deflection-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-part-deflection-heading" className="text-lg font-semibold">Rigidez elástica da peça</h2>
        <span role={partRigidityCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${partRigidityCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-amber-500 bg-amber-950 text-amber-100"}`}>
          {partRigidityCompliant ? "RIGIDEZ DA PEÇA CONFORME" : "ALERTA: DEFLEXÃO EXCESSIVA DA PEÇA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Deflexão teórica máxima" value={`${report.part_elastic_deflection_audit.max_deflection_um.toFixed(3)} µm`} />
        <Metric label="Rigidez calculada" value={`${report.part_elastic_deflection_audit.calculated_stiffness_n_per_mm.toFixed(2)} N/mm`} />
        <Metric label="Comprimento livre" value={`${report.part_elastic_deflection_audit.part_unsupported_length_mm.toFixed(3)} mm`} />
        <Metric label="Diâmetro mínimo" value={`${report.part_elastic_deflection_audit.minimum_diameter_mm.toFixed(3)} mm`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">{report.part_elastic_deflection_audit.deflection_status}</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE FLEXÃO ELÁSTICA DA PEÇA - NÃO CONSIDERA CONTAPONTO OU LUNETA DE APOIO
      </p>
    </section>

    <section aria-labelledby="report-spindle-envelope-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-spindle-envelope-heading" className="text-lg font-semibold">Envelope de potência e torque do fuso</h2>
        <span role={spindleEnvelopeCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${spindleEnvelopeCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {spindleEnvelopeCompliant ? "ENVELOPE DO FUSO CONFORME" : "ALERTA: SOBRECARGA DE TORQUE/POTÊNCIA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Metric label="RPM de corte" value={`${spindleOperatingPoint.spindle_rpm.toFixed(1)} rpm`} />
        <Metric label="Torque requerido" value={`${spindleOperatingPoint.required_torque_nm.toFixed(3)} N.m`} />
        <Metric label="Torque disponível" value={`${spindleOperatingPoint.available_torque_nm.toFixed(3)} N.m`} />
        <Metric label="Potência requerida" value={`${spindleOperatingPoint.required_cutting_power_kw.toFixed(3)} kW`} />
        <Metric label="Potência disponível" value={`${spindleOperatingPoint.available_power_kw.toFixed(3)} kW`} />
      </dl>
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-3">
        <div className="flex items-center justify-between gap-2 text-sm">
          <span>Margem de Reserva do Motor</span>
          <span className="font-mono">{spindleOperatingPoint.power_margin_percent.toFixed(2)}%</span>
        </div>
        <div role="progressbar" aria-label="Margem de Reserva do Motor" aria-valuemin={0} aria-valuemax={100} aria-valuenow={spindleReserve} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
          <div className={spindleEnvelopeCompliant ? "h-full bg-emerald-500" : "h-full bg-red-500"} style={{ width: `${spindleReserve}%` }} />
        </div>
      </div>
      <p className="font-mono text-xs text-slate-300">{report.spindle_power_torque_envelope_audit.audit_status}</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE POTÊNCIA E TORQUE DO FUSO - NÃO CONSIDERA DERATING TÉRMICO CONTÍNUO S1/S6 OU PERDAS POR ENVELHECIMENTO
      </p>
    </section>

    <section aria-labelledby="report-thermal-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-thermal-heading" className="text-lg font-semibold">Expansão térmica e impacto dimensional</h2>
        <span role={thermalDriftTolerated ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${thermalDriftTolerated ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {thermalDriftTolerated ? "DERIVA TÉRMICA TOLERADA" : "ALERTA: DERIVA TÉRMICA EXCEDE TOLERÂNCIA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Temperatura Média Projetada da Peça" value={`${report.thermal_expansion_drift_audit.workpiece_mean_temperature_c.toFixed(1)} °C`} />
        <Metric label="Temperatura Média Projetada do Fuso" value={`${report.thermal_expansion_drift_audit.spindle_mean_temperature_c.toFixed(1)} °C`} />
        <Metric label="Deriva em Z" value={`${report.thermal_expansion_drift_audit.total_z_axis_drift_um.toFixed(3)} µm`} />
        <Metric label="Deriva em X" value={`${report.thermal_expansion_drift_audit.total_x_axis_drift_um.toFixed(3)} µm`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">Impacto dimensional: {thermalImpact.toFixed(2)}% da menor tolerância declarada</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE EXPANSÃO TÉRMICA - NÃO CONSIDERA GRADIENTES TÉRMICOS LOCAIS TRANSITÓRIOS OU COMPENSAÇÃO ATIVA POR REFRIGERAÇÃO INTERNA
      </p>
    </section>

    <section aria-labelledby="report-chip-breaking-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-chip-breaking-heading" className="text-lg font-semibold">Painel de Quebra de Cavaco</h2>
        <span role={chipBreakingSafe ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${chipBreakingSafe ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {chipBreakingSafe ? "FORMAÇÃO SEGURA DE CAVACO" : "ALERTA: RISCO DE CAVACO CONTÍNUO/SOBRECARGA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Geometria Tabulada" value={`${chipBreaking.chipbreaker_family} · ${chipBreaking.chipbreaker_reference}`} />
        <Metric label="Avanço f" value={`${chipBreaking.feed_mm_per_rev.toFixed(3)} mm/rot`} />
        <Metric label="Profundidade ap" value={`${chipBreaking.depth_of_cut_mm.toFixed(3)} mm`} />
        <Metric label="Razão de Compressão de Cavaco" value={chipBreaking.chip_compression_ratio.toFixed(3)} />
      </dl>
      <div aria-label="Envelope visual de quebra de cavaco" className="grid gap-3 rounded-lg border border-slate-700 bg-slate-950 p-3 sm:grid-cols-2">
        <div>
          <div className="flex justify-between text-xs">
            <span>f: {chipBreakingEnvelope.feed_min_mm_per_rev.toFixed(3)}–{chipBreakingEnvelope.feed_max_mm_per_rev.toFixed(3)} mm/rot</span>
            <span>Ponto: {chipBreaking.feed_mm_per_rev.toFixed(3)}</span>
          </div>
          <div role="progressbar" aria-label="Ponto operacional de avanço no envelope" aria-valuemin={0} aria-valuemax={100} aria-valuenow={chipFeedPosition} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
            <div className={chipBreakingSafe ? "h-full bg-emerald-500" : "h-full bg-red-500"} style={{ width: `${chipFeedPosition}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs">
            <span>ap: {chipBreakingEnvelope.depth_of_cut_min_mm.toFixed(3)}–{chipBreakingEnvelope.depth_of_cut_max_mm.toFixed(3)} mm</span>
            <span>Ponto: {chipBreaking.depth_of_cut_mm.toFixed(3)}</span>
          </div>
          <div role="progressbar" aria-label="Ponto operacional de profundidade no envelope" aria-valuemin={0} aria-valuemax={100} aria-valuenow={chipDepthPosition} className="mt-2 h-2 overflow-hidden rounded bg-slate-700">
            <div className={chipBreakingSafe ? "h-full bg-emerald-500" : "h-full bg-red-500"} style={{ width: `${chipDepthPosition}%` }} />
          </div>
        </div>
      </div>
      <p className="font-mono text-xs text-slate-300">
        h={chipBreaking.uncut_chip_thickness_mm.toFixed(4)} mm · b={chipBreaking.chip_width_mm.toFixed(4)} mm · cavaco formado={chipBreaking.formed_chip_thickness_mm.toFixed(4)} mm
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE FORMAÇÃO E QUEBRA DE CAVACO - NÃO CONSIDERA FLUTUAÇÕES DINÂMICAS DE PRESSÃO DE REFRIGERAÇÃO OU VARIAÇÕES MICROESTRUTURAIS
      </p>
    </section>

    <section aria-labelledby="report-coolant-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-coolant-heading" className="text-lg font-semibold">Demanda de fluido por zona térmica</h2>
        <span role={coolantDemandAdequate ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${coolantDemandAdequate ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {coolantDemandAdequate ? "DISSIPAÇÃO TÉRMICA ADEQUADA" : "ALERTA: INSUFFICIENT_THERMAL_DISSIPATION_WARNING"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Modo de fluido" value={coolantAudit.coolant_mode} />
        <Metric label="Vazão programada" value={`${coolantAudit.programmed_flow_l_per_min.toFixed(3)} L/min`} />
        <Metric label="Pressão programada" value={`${coolantAudit.programmed_pressure_bar.toFixed(3)} bar`} />
        <Metric label="Margens vazão / pressão" value={`${coolantAudit.flow_margin_percent.toFixed(2)}% / ${coolantAudit.pressure_margin_percent.toFixed(2)}%`} />
      </dl>
      <div className="overflow-x-auto rounded-lg border border-slate-700">
        <table className="min-w-full divide-y divide-slate-700 text-left text-sm">
          <caption className="sr-only">Requisitos analíticos de vazão e pressão por zona de corte</caption>
          <thead className="bg-slate-950 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th scope="col" className="px-3 py-2">Zona térmica</th>
              <th scope="col" className="px-3 py-2">Vazão mínima</th>
              <th scope="col" className="px-3 py-2">Pressão mínima</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-slate-950/60 font-mono text-cyan-100">
            {coolantAudit.zone_requirements.map((requirement) => <tr key={requirement.cutting_zone}>
              <th scope="row" className="px-3 py-2 font-medium text-slate-200">{requirement.cutting_zone}</th>
              <td className="px-3 py-2">{requirement.minimum_flow_l_per_min.toFixed(3)} L/min</td>
              <td className="px-3 py-2">{requirement.minimum_pressure_bar.toFixed(3)} bar</td>
            </tr>)}
          </tbody>
        </table>
      </div>
      <p className="font-mono text-xs text-slate-300">{coolantAudit.thermal_dissipation_status}</p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE DEMANDA DE FLUIDO - NÃO CONTROLA BOMBAS OU VÁLVULAS DE MÁQUINA
      </p>
    </section>

    <section aria-labelledby="report-workholding-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-workholding-heading" className="text-lg font-semibold">Painel de fixação da placa</h2>
        <span role={dynamicClampingSafe ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${dynamicClampingSafe ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {dynamicClampingSafe ? "FIXAÇÃO DINÂMICA SEGURA" : "ALERTA: PERDA CRÍTICA DE APERTO POR CENTRÍFUGA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Força estática inicial" value={`${(workholdingAudit.static_clamping_force_per_jaw_n * 3 / 1_000).toFixed(3)} kN`} />
        <Metric label="Perda centrífuga calculada" value={`${(workholdingAudit.total_centrifugal_loss_n / 1_000).toFixed(3)} kN`} />
        <Metric label="Força dinâmica residual" value={`${(workholdingAudit.dynamic_clamping_force_total_n / 1_000).toFixed(3)} kN`} />
        <Metric label="Fator de segurança" value={workholdingAudit.clamping_safety_factor.toFixed(2)} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        {workholdingAudit.operating_rpm.toFixed(0)} rpm · μ={workholdingAudit.friction_coefficient.toFixed(3)} · Fz={workholdingAudit.axial_cutting_force_n.toFixed(3)} N · {workholdingAudit.clamping_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE FORÇA DE FIXAÇÃO - NÃO SUBSTITUI VERIFICAÇÃO COM MEDIDOR FÍSICO DE CARGA EM PLACA
      </p>
    </section>

    <section aria-labelledby="report-tailstock-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-tailstock-heading" className="text-lg font-semibold">Painel de contraponto</h2>
        <span role={tailstockSupportCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${tailstockSupportCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {tailstockSupportCompliant ? "APOIO CONFORME" : "ALERTA: RISCO DE FLAMBAGEM POR PRÉ-CARGA"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Força de apoio" value={`${tailstockAudit.tailstock_force_n.toFixed(3)} N`} />
        <Metric label="Carga crítica de flambagem" value={`${tailstockAudit.critical_buckling_load_n.toFixed(3)} N`} />
        <Metric label="Deflexão biapoiada máxima" value={`${tailstockAudit.max_supported_deflection_um.toFixed(3)} µm`} />
        <Metric label="Cota de engajamento Z" value={`${tailstockAudit.engagement_z_coordinate_mm.toFixed(3)} mm`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        L={tailstockAudit.total_supported_length_mm.toFixed(3)} mm · Fr={tailstockAudit.radial_cutting_force_n.toFixed(3)} N · limite 30%={tailstockAudit.warning_threshold_n.toFixed(3)} N · {tailstockAudit.tailstock_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE CARGA E APOIO DE CONTRAPONTO - NÃO CONSIDERA EXCENTRICIDADE DO PONTO DE CENTRO OU DESGASTE DE ROLAMENTOS DO MANGOTE
      </p>
    </section>

    <section aria-labelledby="report-harmonic-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-harmonic-heading" className="text-lg font-semibold">Painel de Dinâmica Rotativa</h2>
        <span role={spindleDynamicsCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${spindleDynamicsCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {spindleDynamicsBadge}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Rotação Crítica de Ressonância" value={`${harmonicAudit.first_critical_rpm.toFixed(3)} RPM`} />
        <Metric label="Rotação Programada" value={`${harmonicAudit.operating_rpm.toFixed(3)} RPM`} />
        <Metric label="Proximidade Harmônica" value={`${harmonicAudit.resonance_proximity_percent.toFixed(3)}%`} />
        <Metric label="Força Dinâmica de Desbalanceamento" value={`${harmonicAudit.unbalance_force_n.toFixed(3)} N`} />
      </dl>
      <div className="space-y-1" aria-label="Proximidade da rotação crítica">
        <div className="relative h-4 overflow-hidden rounded-full border border-slate-600 bg-slate-800">
          <div className="absolute inset-y-0 left-0 w-1/2 bg-red-700" aria-label="Zona vermelha de exclusão operacional até 15%" />
          <div className="absolute inset-y-0 left-1/2 right-0 bg-emerald-800" />
          <span className="absolute top-0 h-full w-1 bg-white" style={{ left: `${harmonicMarkerPosition}%` }} />
        </div>
        <p className="font-mono text-xs text-slate-300">
          faixa de exclusão ±{harmonicAudit.resonance_exclusion_percent.toFixed(1)}% · limite dos mancais {harmonicAudit.bearing_admissible_force_n.toFixed(3)} N · {harmonicAudit.dynamic_status}
        </p>
      </div>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        ESTIMATIVA ANALÍTICA DE VELOCIDADE CRÍTICA E RESSONÂNCIA - NÃO CONSIDERA AMORTECIMENTO VISCOSO DO FUSO OU DEFEITOS EM PISTAS DE ROLAMENTO
      </p>
    </section>

    <section aria-labelledby="report-jaw-pressure-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-jaw-pressure-heading" className="text-lg font-semibold">Pressão de contato das castanhas</h2>
        <span role={jawPressureCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${jawPressureCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {jawPressureBadge}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Área nominal de contato" value={`${jawPressureAudit.contact_area_mm2.toFixed(3)} mm²`} />
        <Metric label="Pressão média de contato" value={`${jawPressureAudit.mean_contact_pressure_mpa.toFixed(3)} MPa`} />
        <Metric label="Limite de escoamento" value={`${jawPressureAudit.material_yield_strength_mpa.toFixed(3)} MPa`} />
        <Metric label="Razão de carregamento" value={`${jawPressureAudit.pressure_ratio_percent.toFixed(2)}%`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        pressão mínima de retenção {jawPressureAudit.minimum_retention_pressure_mpa.toFixed(3)} MPa · força dinâmica por castanha {jawPressureAudit.dynamic_force_per_jaw_n.toFixed(3)} N · {jawPressureAudit.clamping_pressure_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        {jawPressureAudit.model_limitation}
      </p>
    </section>

    <section aria-labelledby="report-guideway-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-guideway-heading" className="text-lg font-semibold">Painel de Carga no Barramento</h2>
        <span role={guidewayCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${guidewayCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {guidewayCompliant ? "GUIAS DENTRO DO ENVELOPE ESTÁVEL" : "ALERTA: SOBRECARGA DINÂMICA NOS GUIAS"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Metric label="Momento Mx · rolamento" value={`${guidewayAudit.rolling_moment_nm.toFixed(3)} N·m`} />
        <Metric label="Momento My · arfagem" value={`${guidewayAudit.pitching_moment_nm.toFixed(3)} N·m`} />
        <Metric label="Momento Mz · guinada" value={`${guidewayAudit.yawing_moment_nm.toFixed(3)} N·m`} />
        <Metric label="Carga máxima por patim" value={`${guidewayAudit.max_block_load_n.toFixed(3)} N`} />
        <Metric label="Capacidade nominal C0" value={`${guidewayAudit.static_capacity_n.toFixed(3)} N`} />
        <Metric label="Relação de carga" value={`${guidewayAudit.load_ratio_percent.toFixed(2)}%`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        Fc={guidewayAudit.tangential_cutting_force_n.toFixed(3)} N · Ff={guidewayAudit.axial_feed_force_n.toFixed(3)} N · Fr={guidewayAudit.radial_cutting_force_n.toFixed(3)} N · {guidewayAudit.guideway_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        {guidewayAudit.model_limitation}
      </p>
    </section>

    <section aria-labelledby="report-ballscrew-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-ballscrew-heading" className="text-lg font-semibold">Auditoria mecânica do fuso de esferas</h2>
        <span role={ballscrewCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${ballscrewCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {ballscrewCompliant ? "FUSO DE ESFERAS EM REGIME SEGURO" : "ALERTA: RISCO DE FLAMBAGEM OU VELOCIDADE CRÍTICA DO FUSO"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Empuxo axial total" value={`${ballscrewAudit.total_axial_thrust_n.toFixed(3)} N`} />
        <Metric label="Limite de flambagem" value={`${ballscrewAudit.euler_buckling_limit_n.toFixed(3)} N`} />
        <Metric label="Rotação do fuso" value={`${ballscrewAudit.operating_ballscrew_rpm.toFixed(3)} / ${ballscrewAudit.critical_speed_rpm.toFixed(3)} RPM`} />
        <Metric label="Relação de carga" value={`${ballscrewAudit.load_ratio_percent.toFixed(2)}%`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        velocidade relativa {ballscrewAudit.speed_ratio_percent.toFixed(2)}% · {ballscrewAudit.ballscrew_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        {ballscrewAudit.model_limitation}
      </p>
    </section>

    <section aria-labelledby="report-spindle-bearing-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-spindle-bearing-heading" className="text-lg font-semibold">Carga térmica nos rolamentos do fuso</h2>
        <span role={spindleBearingCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${spindleBearingCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {spindleBearingCompliant ? "TEMPERATURA DE MANCAIS ESTÁVEL" : "ALERTA: RISCO DE SUPERAQUECIMENTO NOS ROLAMENTOS"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Torque total de atrito" value={`${spindleBearingAudit.total_friction_torque_nm.toFixed(3)} N·m`} />
        <Metric label="Calor dissipado" value={`${spindleBearingAudit.total_heat_dissipated_w.toFixed(3)} W`} />
        <Metric label="Temperatura estimada" value={`${spindleBearingAudit.estimated_bearing_temp_c.toFixed(3)} °C`} />
        <Metric label="Limite térmico do lubrificante" value={`${spindleBearingAudit.max_admissible_temp_c.toFixed(3)} °C`} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        carga {spindleBearingAudit.load_torque_nm.toFixed(3)} N·m · viscoso {spindleBearingAudit.viscous_torque_nm.toFixed(3)} N·m · {spindleBearingAudit.bearing_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        {spindleBearingAudit.model_limitation}
      </p>
    </section>

    <section aria-labelledby="report-bearing-life-heading" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="report-bearing-life-heading" className="text-lg font-semibold">Vida útil L10h dos rolamentos do fuso</h2>
        <span role={bearingLifeCompliant ? "status" : "alert"} className={`rounded-full border px-3 py-1 text-xs font-bold ${bearingLifeCompliant ? "border-emerald-500 bg-emerald-950 text-emerald-100" : "border-red-500 bg-red-950 text-red-100"}`}>
          {bearingLifeCompliant ? "VIDA ÚTIL DO MANCAL CONFORME" : "ALERTA: FADIGA PREMATURA DE ROLAMENTO"}
        </span>
      </div>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Carga dinâmica equivalente" value={`${bearingLifeAudit.equivalent_dynamic_load_n.toFixed(3)} N`} />
        <Metric label="L10" value={`${bearingLifeAudit.l10_million_revs.toFixed(3)} milhões de revoluções`} />
        <Metric label="Vida projetada L10h" value={`${bearingLifeAudit.l10h_hours.toFixed(3)} h`} />
        <Metric label="Razão de viscosidade kappa" value={bearingLifeAudit.viscosity_ratio_kappa.toFixed(3)} />
      </dl>
      <p className="font-mono text-xs text-slate-300">
        aISO {bearingLifeAudit.a_iso_modification_factor.toFixed(3)} · C {bearingLifeAudit.dynamic_capacity_c_n.toFixed(3)} N · {bearingLifeAudit.bearing_life_status}
      </p>
      <p className="rounded-lg border border-amber-500 bg-amber-950/60 p-3 text-xs font-semibold text-amber-100">
        {bearingLifeAudit.model_limitation}
      </p>
    </section>

    <section aria-labelledby="report-limits-heading" className="space-y-2">
      <h2 id="report-limits-heading" className="text-lg font-semibold">Limitações obrigatórias</h2>
      <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
        {report.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}
      </ul>
      <p className="text-xs font-semibold text-amber-200">G9=PENDING_AUTHORITATIVE_REVIEW · CONTROLLER_PROFILE_UNRESOLVED · executable_output=false</p>
    </section>
  </article>;
}
