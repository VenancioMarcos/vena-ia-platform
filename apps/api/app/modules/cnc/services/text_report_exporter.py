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
