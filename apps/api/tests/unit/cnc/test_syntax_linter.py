from app.modules.cnc.enums import CNCControllerType
from app.modules.cnc.services.syntax_linter import audit_gcode_syntax


HEADER = "\n".join(
    (
        "(GOVERNANCE: PHYSICAL_USE_AUTHORIZED=FALSE)",
        "(GOVERNANCE: G9=PENDING_AUTHORITATIVE_REVIEW)",
        "(GOVERNANCE: NO_HUMAN_REVIEW_BYPASS=TRUE)",
        "(NOTICE: NON-EXECUTABLE AUDIT CODE ONLY)",
        "(SAFETY: MACHINE_SEND=FALSE DNC=FALSE NC_TRANSFER=FALSE CYCLE_START=FALSE)",
        "(SAFETY: emission_status=CONTROLLER_PROFILE_UNRESOLVED)",
        "(SAFETY: executable_output=false)",
    )
)


def _program(profile: CNCControllerType, body: str = "G01 X20 Z-10 F0.2\nM30") -> str:
    start = '%_N_VENA_9001_MPF\nT="FERRAMENTA" D1' if profile is CNCControllerType.SIEMENS_840D else "O9001\nT0101"
    return f"{start}\n{HEADER}\n{body}\n%"


def test_accepts_well_formed_fanuc_siemens_and_haas_profiles() -> None:
    for profile in (CNCControllerType.FANUC_0I, CNCControllerType.SIEMENS_840D, CNCControllerType.HAAS):
        audit = audit_gcode_syntax(_program(profile), profile)
        assert audit.status == "VALID"
        assert audit.violations == ()


def test_rejects_conflicting_motion_codes_with_line_evidence() -> None:
    audit = audit_gcode_syntax(_program(CNCControllerType.FANUC_0I, "G00 G01 X20 Z-10 F0.2\nM30"), CNCControllerType.FANUC_0I)
    assert audit.status == "REJECTED"
    assert any(item.code == "CONFLICTING_MODAL_MOTION" and item.line_number > 0 for item in audit.violations)


def test_rejects_missing_governance_header_fail_closed() -> None:
    audit = audit_gcode_syntax("O9001\nT0101\nG01 X20 Z-10 F0.2\nM30\n%", CNCControllerType.FANUC_0I)
    assert audit.status == "REJECTED"
    assert {item.code for item in audit.violations} == {"GOVERNANCE_HEADER_MISSING"}


def test_rejects_dialect_specific_invalid_tool_call_and_nonpositive_feed() -> None:
    audit = audit_gcode_syntax(_program(CNCControllerType.HAAS, "T1\nG01 X20 Z-10 F0\nM30"), CNCControllerType.HAAS)
    assert {item.code for item in audit.violations} == {"TOOL_CALL_INVALID", "NON_POSITIVE_FEED_OR_SPINDLE"}
