"""Deterministic human-readable export for analytical CNC reports."""

from app.modules.cnc.schemas import MachiningTechnicalReportPayload


SAFETY_STAMP = "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO"


def _section(title: str, lines: tuple[str, ...]) -> str:
    return "\n".join((f"[{title}]", SAFETY_STAMP, *lines))


def format_machining_report_text(report: MachiningTechnicalReportPayload) -> str:
    """Render approved analytical evidence without emitting controller program data."""
    validated = MachiningTechnicalReportPayload.model_validate(report)
    audit = validated.geometry_audit
    sections = (
        _section(
            "IDENTIFICAÇÃO",
            (
                f"schema_version={validated.schema_version}",
                f"plan_id={validated.plan_id}",
                f"cad_job_id={validated.cad_job_id}",
                f"analytical_snapshot_at={validated.analytical_snapshot_at.isoformat()}",
                f"program_sha256={validated.program_sha256}",
            ),
        ),
        _section(
            "AUDITORIA DIMENSIONAL",
            (
                f"status={audit.status}",
                f"manifest_generation_allowed={str(audit.manifest_generation_allowed).lower()}",
                *(
                    f"{item.axis}: nominal_mm={item.nominal_mm:.9f}; "
                    f"programmed_mm={item.programmed_mm:.9f}; "
                    f"signed_deviation_mm={item.signed_deviation_mm:.9f}; "
                    f"tolerance_mm={item.tolerance_mm:.9f}; "
                    f"within_tolerance={str(item.within_tolerance).lower()}"
                    for item in audit.deviations
                ),
            ),
        ),
        _section(
            "MÉTRICAS ANALÍTICAS",
            (
                "total_cycle_time_seconds="
                f"{validated.cycle_time_estimate.total_cycle_time_seconds:.9f}",
                f"total_distance_mm={validated.total_distance_mm:.9f}",
                f"envelope_audit={validated.envelope_audit}",
                f"minimum_chuck_clearance_mm={validated.chuck_proximity.minimum_clearance_mm:.9f}",
                "surface_ra_theoretical_um="
                f"{validated.surface_roughness_audit.ra_theoretical_um:.9f}",
                "surface_rz_theoretical_um="
                f"{validated.surface_roughness_audit.rz_theoretical_um:.9f}",
                "surface_roughness_compliance="
                f"{validated.surface_roughness_audit.compliance_tag}",
                f"cutting_force_nominal_n={validated.power_force_audit.fc_nominal_n:.9f}",
                f"cutting_power_kw={validated.power_force_audit.pc_cutting_kw:.9f}",
                f"motor_power_est_kw={validated.power_force_audit.p_motor_est_kw:.9f}",
                f"material_removal_rate_cm3_min={validated.power_force_audit.mrr_cm3_min:.9f}",
                f"power_status={validated.power_force_audit.power_status}",
                "ESTIMATIVA ENERGÉTICA ANALÍTICA DE KIENZLE - NÃO CONSIDERA "
                "RENDIMENTO DINÂMICO REAL",
                *(
                    f"tool_life[{item.tool_id}]: estimated_minutes="
                    f"{item.estimated_tool_life_minutes:.9f}; consumed_percent="
                    f"{item.tool_life_consumed_percent:.9f}; status={item.integrity_status}"
                    for item in validated.tool_life_audits
                ),
                "ESTIMATIVA ANALÍTICA DE TAYLOR - NÃO CONSIDERA FLUTUAÇÕES "
                "TÉRMICAS REAIS OU LUBRIFICAÇÃO",
                "cost_time: total_minutes="
                f"{validated.cost_time_audit.total_cycle_time_minutes:.9f}; "
                f"machine_cost={validated.cost_time_audit.machine_cost_component:.9f}; "
                f"tooling_cost={validated.cost_time_audit.tooling_wear_cost_component:.9f}; "
                f"total_cost={validated.cost_time_audit.estimated_total_cost:.9f}; "
                f"currency={validated.cost_time_audit.currency}",
                "ESTIMATIVA ECONÔMICA E DE TEMPO ANALÍTICA - NÃO CONSIDERA "
                "FLUTUAÇÕES LOGÍSTICAS, PARADAS NÃO PROGRAMADAS OU IMPOSTOS",
                "sustainability: electrical_energy_kwh="
                f"{validated.sustainability_audit.electrical_energy_kwh:.9f}; "
                f"cutting_energy_kwh={validated.sustainability_audit.cutting_energy_kwh:.9f}; "
                f"standby_energy_kwh={validated.sustainability_audit.standby_energy_kwh:.9f}; "
                f"carbon_emission_kg_co2e="
                f"{validated.sustainability_audit.carbon_emission_kg_co2e:.9f}; "
                f"grid_region={validated.sustainability_audit.grid_region}",
                "ESTIMATIVA ECOLÓGICA E ENERGÉTICA ANALÍTICA - NÃO CONSIDERA "
                "DINÂMICA AUXILIAR DE REFRIGERAÇÃO EXTERNA OU PICOS DE PARTIDA",
                *(
                    f"stability[{item.tool_id}]: overhang_ratio_l_d="
                    f"{item.overhang_ratio_l_d:.9f}; static_deflection_um="
                    f"{item.static_deflection_um:.9f}; stiffness_n_per_mm="
                    f"{item.equivalent_stiffness_n_per_mm:.9f}; "
                    f"stability_limit_depth_mm={item.stability_limit_depth_mm:.9f}; "
                    f"status={item.stability_status}"
                    for item in validated.stability_audits
                ),
                "ESTIMATIVA ANALÍTICA DE ESTABILIDADE DINÂMICA - NÃO CONSIDERA "
                "MODOS DE VIBRAÇÃO DA PEÇA OU DO FUSO",
                *(
                    f"parameter_optimization[{item.tool_id}]: programmed_vc_m_min="
                    f"{item.programmed_vc_m_min:.9f}; programmed_feed_mm_rev="
                    f"{item.programmed_feed_mm_rev:.9f}; programmed_ap_mm="
                    f"{item.programmed_ap_mm:.9f}; recommended_vc_m_min="
                    f"{item.recommended_vc_m_min}; recommended_feed_mm_rev="
                    f"{item.recommended_feed_mm_rev}; recommended_ap_mm="
                    f"{item.recommended_ap_mm}; predicted_mrr_cm3_min="
                    f"{item.predicted_mrr_cm3_min}; status={item.optimization_status}"
                    for item in validated.parameter_optimizations
                ),
                "SUGESTÃO ANALÍTICA DE PARÂMETROS DE CORTE - APLICAÇÃO EM MÁQUINA "
                "REQUER HOMOLOGAÇÃO MANUAL POR ENGENHARIA DE PROCESSOS",
                "risk_matrix: overall_score="
                f"{validated.risk_matrix.overall_risk_score:.9f}; "
                f"risk_level={validated.risk_matrix.risk_level}; "
                f"dimensional_score={validated.risk_matrix.dimensional_risk_score:.9f}; "
                f"dynamic_score={validated.risk_matrix.dynamic_risk_score:.9f}; "
                f"energy_score={validated.risk_matrix.energy_risk_score:.9f}; "
                f"tool_wear_score={validated.risk_matrix.tool_wear_risk_score:.9f}",
                *(
                    f"risk_mitigation[{index}]={recommendation}"
                    for index, recommendation in enumerate(
                        validated.risk_matrix.mitigation_recommendations,
                        start=1,
                    )
                ),
                "MATRIZ DE RISCO ANALÍTICA CONSOLIDADA - AVALIAÇÃO PRELIMINAR DE "
                "PROCESSO SEM VALIDADE DE LAUDO PERICIAL",
            ),
        ),
        _section(
            "FOLHA DE PROCESSO",
            (
                f"part_id={validated.process_sheet.part_id}",
                f"revision={validated.process_sheet.revision}",
                "raw_stock: diameter_mm="
                f"{validated.process_sheet.raw_stock_dimensions.diameter_mm:.9f}; "
                "axial_length_mm="
                f"{validated.process_sheet.raw_stock_dimensions.axial_length_mm:.9f}",
                "clamping: setup_type="
                f"{validated.process_sheet.clamping_setup.setup_type}; "
                "minimum_clearance_mm="
                f"{validated.process_sheet.clamping_setup.minimum_clearance_mm:.9f}; "
                f"balance={validated.process_sheet.clamping_setup.balance_requirement}",
                *(
                    f"operation[{item.sequence}]: id={item.operation_id}; phase={item.phase}; "
                    f"tool={item.tool_id}; insert={item.insert_reference}; "
                    f"vc_m_min={item.cutting_speed_vc_m_per_min}; "
                    f"feed_mm_rev={item.feed_mm_per_rev}; ap_mm={item.depth_of_cut_ap_mm}; "
                    f"rpm={item.spindle_rpm}; feed_rate_mm_min={item.feed_rate_mm_min}; "
                    f"estimated_time_min={item.estimated_time_min:.9f}"
                    for item in validated.process_sheet.sequence_operations
                ),
                *(
                    f"safety_instruction[{index}]={instruction}"
                    for index, instruction in enumerate(
                        validated.process_sheet.safety_instructions,
                        start=1,
                    )
                ),
                "FOLHA DE PROCESSO TEÓRICA ANALÍTICA - DOCUMENTO ORIENTATIVO SUJEITO À "
                "APROVAÇÃO DO PREPARADOR DE MÁQUINAS",
            ),
        ),
        _section(
            "AUDITORIA DE MATERIAL REMANESCENTE",
            (
                f"status={validated.residual_stock_audit.status}",
                f"max_residual_stock_mm={validated.residual_stock_audit.max_residual_stock_mm:.9f}",
                f"min_residual_stock_mm={validated.residual_stock_audit.min_residual_stock_mm:.9f}",
                "average_stock_allowance_mm="
                f"{validated.residual_stock_audit.average_stock_allowance_mm:.9f}",
                f"gouging_detected={str(validated.residual_stock_audit.gouging_detected).lower()}",
                *(
                    f"residual_section[{index}]: front_z_mm={item.front_z_mm:.9f}; "
                    f"rear_z_mm={item.rear_z_mm:.9f}; "
                    f"nominal_radius_mm={item.nominal_radius_mm:.9f}; "
                    f"in_process_radius_mm={item.in_process_radius_mm:.9f}; "
                    f"residual_stock_mm={item.residual_stock_mm:.9f}"
                    for index, item in enumerate(
                        validated.residual_stock_audit.sections,
                        start=1,
                    )
                ),
                "AUDITORIA ANALÍTICA DE MATERIAL REMANESCENTE - NÃO SUBSTITUI "
                "MEDIÇÃO TRIDIMENSIONAL FÍSICA EM CMM",
            ),
        ),
        _section(
            "FLEXÃO ELÁSTICA DA PEÇA",
            (
                "part_unsupported_length_mm="
                f"{validated.part_elastic_deflection_audit.part_unsupported_length_mm:.9f}",
                "minimum_diameter_mm="
                f"{validated.part_elastic_deflection_audit.minimum_diameter_mm:.9f}",
                "radial_cutting_force_N="
                f"{validated.part_elastic_deflection_audit.radial_cutting_force_n:.9f}",
                "young_modulus_mpa="
                f"{validated.part_elastic_deflection_audit.young_modulus_mpa:.9f}",
                "calculated_stiffness_n_per_mm="
                f"{validated.part_elastic_deflection_audit.calculated_stiffness_n_per_mm:.9f}",
                "max_deflection_um="
                f"{validated.part_elastic_deflection_audit.max_deflection_um:.9f}",
                "radial_tolerance_mm="
                f"{validated.part_elastic_deflection_audit.radial_tolerance_mm:.9f}",
                "deflection_status="
                f"{validated.part_elastic_deflection_audit.deflection_status}",
                "ESTIMATIVA ANALÍTICA DE FLEXÃO ELÁSTICA DA PEÇA - NÃO CONSIDERA "
                "CONTAPONTO OU LUNETA DE APOIO",
            ),
        ),
        _section(
            "ENVELOPE DE POTÊNCIA E TORQUE DO FUSO",
            (
                f"status={validated.spindle_power_torque_envelope_audit.audit_status}",
                "spindle_rpm_min="
                f"{validated.spindle_power_torque_envelope_audit.spindle_rpm_min:.9f}",
                "spindle_rpm_max="
                f"{validated.spindle_power_torque_envelope_audit.spindle_rpm_max:.9f}",
                *(
                    f"operating_point[{index}]: spindle_rpm={item.spindle_rpm:.9f}; "
                    f"required_torque_nm={item.required_torque_nm:.9f}; "
                    f"available_torque_nm={item.available_torque_nm:.9f}; "
                    f"required_power_kw={item.required_cutting_power_kw:.9f}; "
                    f"available_power_kw={item.available_power_kw:.9f}; "
                    f"power_margin_percent={item.power_margin_percent:.9f}; "
                    f"status={item.status}"
                    for index, item in enumerate(
                        validated.spindle_power_torque_envelope_audit.operating_points,
                        start=1,
                    )
                ),
                "ESTIMATIVA ANALÍTICA DE POTÊNCIA E TORQUE DO FUSO - NÃO CONSIDERA "
                "DERATING TÉRMICO CONTÍNUO S1/S6 OU PERDAS POR ENVELHECIMENTO",
            ),
        ),
        _section(
            "GOVERNANÇA",
            (
                "PHYSICAL_USE_AUTHORIZED=FALSE",
                "G9=PENDING_AUTHORITATIVE_REVIEW",
                "NO_HUMAN_REVIEW_BYPASS=TRUE",
                "MACHINE_SEND=false",
                "DNC=false",
                "NC_TRANSFER=false",
                "CYCLE_START=false",
                "emission_status=CONTROLLER_PROFILE_UNRESOLVED",
                "executable_output=false",
            ),
        ),
        _section("LIMITAÇÕES", tuple(validated.limitations)),
    )
    return "\n\n".join(sections) + "\n"


__all__ = ("SAFETY_STAMP", "format_machining_report_text")
