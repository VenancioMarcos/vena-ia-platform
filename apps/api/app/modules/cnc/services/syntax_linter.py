"""Fail-closed static syntax audit for non-executable CNC candidates.

The linter never executes, transmits, or approves a program for machine use.
It only reports whether a deterministic candidate satisfies the limited dialect
profile and its mandatory governance header.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.modules.cnc.enums import CNCControllerType


REQUIRED_GOVERNANCE_COMMENTS = frozenset(
    {
        "(GOVERNANCE: PHYSICAL_USE_AUTHORIZED=FALSE)",
        "(GOVERNANCE: G9=PENDING_AUTHORITATIVE_REVIEW)",
        "(GOVERNANCE: NO_HUMAN_REVIEW_BYPASS=TRUE)",
        "(NOTICE: NON-EXECUTABLE AUDIT CODE ONLY)",
        "(SAFETY: MACHINE_SEND=FALSE DNC=FALSE NC_TRANSFER=FALSE CYCLE_START=FALSE)",
        "(SAFETY: emission_status=CONTROLLER_PROFILE_UNRESOLVED)",
        "(SAFETY: executable_output=false)",
    }
)
_WORD_RE = re.compile(r"(?:G\d{1,3}|M\d{1,3}|LIMS=\d+(?:\.\d+)?|[FS]-?\d+(?:\.\d+)?|T(?:\d{1,4}|=\"[^\"]+\"\s+D\d+))")
_PROGRAM_RE = re.compile(r"^O\d{1,8}$")
_SIEMENS_PROGRAM_RE = re.compile(r"^%_N_[A-Z0-9_]+_MPF$")
_FANUC_TOOL_RE = re.compile(r"^T\d{4}$")
_SIEMENS_TOOL_RE = re.compile(r'^T="[A-Za-z0-9 _-]+" D\d{1,2}$')


@dataclass(frozen=True)
class SyntaxViolation:
    line_number: int
    code: str
    message: str


@dataclass(frozen=True)
class GCodeSyntaxAudit:
    status: str
    controller_profile: CNCControllerType
    violations: tuple[SyntaxViolation, ...]


def _violation(line: int, code: str, message: str) -> SyntaxViolation:
    return SyntaxViolation(line, code, message)


def audit_gcode_syntax(
    program_text: str, controller_profile: CNCControllerType
) -> GCodeSyntaxAudit:
    """Audit a limited, generated program profile without executing its contents."""
    violations: list[SyntaxViolation] = []
    lines = tuple(line.strip() for line in program_text.splitlines() if line.strip())
    if not lines:
        return GCodeSyntaxAudit(
            "REJECTED",
            controller_profile,
            (_violation(0, "PROGRAM_EMPTY", "Program text is required."),),
        )

    actual_comments = frozenset(line for line in lines if line.startswith("("))
    for comment in sorted(REQUIRED_GOVERNANCE_COMMENTS - actual_comments):
        violations.append(_violation(0, "GOVERNANCE_HEADER_MISSING", comment))

    expected_program = _SIEMENS_PROGRAM_RE if controller_profile is CNCControllerType.SIEMENS_840D else _PROGRAM_RE
    if not expected_program.fullmatch(lines[0]):
        violations.append(_violation(1, "PROGRAM_NUMBER_INVALID", "Program identifier does not match dialect."))

    for line_number, line in enumerate(lines, start=1):
        if line.startswith("(") or line == "%" or line.startswith("O") or line.startswith("%_"):
            continue
        words = _WORD_RE.findall(line)
        if not words:
            violations.append(_violation(line_number, "BLOCK_SYNTAX_INVALID", line))
            continue
        g_codes = {word for word in words if word.startswith("G")}
        if "G00" in g_codes and "G01" in g_codes or "G0" in g_codes and "G1" in g_codes:
            violations.append(_violation(line_number, "CONFLICTING_MODAL_MOTION", line))
        feed_words = [word for word in words if word.startswith("F")]
        spindle_words = [word for word in words if word.startswith("S")]
        if any(float(word[1:]) <= 0 for word in (*feed_words, *spindle_words)):
            violations.append(_violation(line_number, "NON_POSITIVE_FEED_OR_SPINDLE", line))
        if line.startswith("T"):
            valid_tool = (
                _SIEMENS_TOOL_RE.fullmatch(line)
                if controller_profile is CNCControllerType.SIEMENS_840D
                else _FANUC_TOOL_RE.fullmatch(line)
            )
            if not valid_tool:
                violations.append(_violation(line_number, "TOOL_CALL_INVALID", line))

    return GCodeSyntaxAudit(
        "VALID" if not violations else "REJECTED", controller_profile, tuple(violations)
    )


class GCodeSyntaxAuditError(ValueError):
    """Raised when a candidate fails the static fail-closed syntax audit."""


def require_valid_gcode_syntax(program_text: str, controller_profile: CNCControllerType) -> GCodeSyntaxAudit:
    audit = audit_gcode_syntax(program_text, controller_profile)
    if audit.status != "VALID":
        codes = ",".join(violation.code for violation in audit.violations)
        raise GCodeSyntaxAuditError(f"GCODE_SYNTAX_AUDIT_REJECTED:{codes}")
    return audit
