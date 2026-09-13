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
                f"total_cycle_time_seconds={validated.cycle_time_estimate.total_cycle_time_seconds:.9f}",
                f"total_distance_mm={validated.total_distance_mm:.9f}",
                f"envelope_audit={validated.envelope_audit}",
                f"minimum_chuck_clearance_mm={validated.chuck_proximity.minimum_clearance_mm:.9f}",
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
