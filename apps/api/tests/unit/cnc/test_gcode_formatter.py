from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import MachiningPass, RzPoint, TurningStrategyPlanResponse
from app.modules.cnc.enums import CNCControllerType, FeedMode, SpindleMode
from app.modules.cnc.schemas import GCodeGenerationRequest
from app.modules.cnc.services.gcode_formatter import GCodeFormattingError, format_gcode_candidate


def _plan() -> TurningStrategyPlanResponse:
    return TurningStrategyPlanResponse(
        operation_type=TurningOperationType.ROUGH_TURNING,
        passes=(
            MachiningPass(
                sequence=1,
                operation_type=TurningOperationType.ROUGH_TURNING,
                coordinates_rz_mm=(
                    RzPoint(r_mm=12.0, z_mm=2.0),
                    RzPoint(r_mm=10.0, z_mm=2.0),
                    RzPoint(r_mm=10.0, z_mm=-20.0),
                ),
                estimated_removed_volume_mm3=1_000.0,
            ),
        ),
        material_removal_volume_mm3=1_000.0,
        warnings=("ANALYTICAL_2D_REQUIRES_HUMAN_REVIEW",),
    )


def _request(**updates: object) -> GCodeGenerationRequest:
    values: dict[str, object] = {
        "plan_id": "plan-test-001",
        "cam_plan_data": _plan(),
        "controller_profile": CNCControllerType.FANUC_0I,
        "program_number": 9001,
        "machine_envelope": {
            "x_min_mm": 0.0,
            "x_max_mm": 100.0,
            "z_min_mm": -200.0,
            "z_max_mm": 200.0,
            "chuck_exclusion_zone": {
                "x_min_mm": 0.0,
                "x_max_mm": 100.0,
                "z_min_mm": 50.0,
                "z_max_mm": 100.0,
            },
        },
        "review_authentication": "AUTHENTICATED_REVIEW_CONTEXT",
    }
    values.update(updates)
    return GCodeGenerationRequest(**values)


def test_formats_deterministic_iso_turning_candidate() -> None:
    first = format_gcode_candidate(_request())
    second = format_gcode_candidate(_request())

    assert first == second
    assert first.status == "PLANNED_REQUIRES_REVIEW"
    assert first.program_text.startswith("O9001\n(VENA_IA PLAN_ID=plan-test-001)")
    assert "\nG21\nG18\nG95\nG97 S1000\n" in first.program_text
    assert "G00 X24 Z2" in first.program_text
    assert "G01 X20 Z2 F0.2" in first.program_text
    assert "G01 X20 Z-20 F0.2" in first.program_text
    assert first.program_text.endswith("M05\nM30\n%")
    assert first.metadata.path_length_mm == pytest.approx(26.0)
    assert first.metadata.motion_block_count == 3


def test_program_contains_all_mandatory_safety_invariants() -> None:
    result = format_gcode_candidate(_request(controller_profile=CNCControllerType.SIMULATED_STUB))

    assert "(GOVERNANCE: PHYSICAL_USE_AUTHORIZED=FALSE)" in result.program_text
    assert "(GOVERNANCE: G9=PENDING_AUTHORITATIVE_REVIEW)" in result.program_text
    assert "(GOVERNANCE: NO_HUMAN_REVIEW_BYPASS=TRUE)" in result.program_text
    assert "(NOTICE: NON-EXECUTABLE AUDIT CODE ONLY)" in result.program_text
    assert "(SAFETY: PHYSICAL_USE_AUTHORIZED=FALSE)" in result.program_text
    assert "(SAFETY: G9=PENDING_AUTHORITATIVE_REVIEW)" in result.program_text
    assert "(SAFETY: NO_HUMAN_REVIEW_BYPASS=TRUE)" in result.program_text
    assert "MACHINE_SEND=FALSE DNC=FALSE NC_TRANSFER=FALSE CYCLE_START=FALSE" in result.program_text
    assert "emission_status=CONTROLLER_PROFILE_UNRESOLVED" in result.program_text
    assert "executable_output=false" in result.program_text
    assert result.safety_flags.physical_use_authorized is False
    assert result.safety_flags.no_human_review_bypass is True
    assert result.safety_flags.executable_output is False


def test_rejects_unsupported_controller_profile_fail_closed() -> None:
    with pytest.raises(ValidationError, match="controller_profile"):
        _request(controller_profile="GENERIC_UNVERIFIED")


def test_rejects_missing_review_authentication_fail_closed() -> None:
    values = _request().model_dump()
    values.pop("review_authentication")

    with pytest.raises(ValidationError, match="review_authentication"):
        GCodeGenerationRequest(**values)


def test_formats_fanuc_0i_dialect_with_tool_and_css_limit() -> None:
    result = format_gcode_candidate(
        _request(
            controller_profile=CNCControllerType.FANUC_0I,
            spindle_mode=SpindleMode.G96_CONSTANT_SURFACE_SPEED,
            max_spindle_rpm=2_500.0,
            tool_number=7,
            tool_offset=3,
        )
    )

    assert result.program_text.startswith("O9001")
    assert "\nT0703\nG21\nG18\nG95\nG50 S2500\nG96 S1000\n" in result.program_text
    assert "G00 X24 Z2" in result.program_text
    assert "G01 X20 Z2 F0.2" in result.program_text


def test_formats_siemens_840d_dialect_with_named_tool_and_lims() -> None:
    result = format_gcode_candidate(
        _request(
            controller_profile=CNCControllerType.SIEMENS_840D,
            spindle_mode=SpindleMode.G96_CONSTANT_SURFACE_SPEED,
            max_spindle_rpm=2_200.0,
            tool_name="FERRAMENTA",
            tool_offset=1,
        )
    )

    assert result.program_text.startswith("%_N_VENA_9001_MPF")
    assert 'T="FERRAMENTA" D1' in result.program_text
    assert "\nLIMS=2200\nG96 S1000\n" in result.program_text
    assert "G0 X24 Z2" in result.program_text
    assert "G1 X20 Z2 F0.2" in result.program_text


def test_formats_haas_dialect_with_clean_termination() -> None:
    result = format_gcode_candidate(
        _request(controller_profile=CNCControllerType.HAAS, tool_number=2, tool_offset=2)
    )

    assert result.program_text.startswith("O9001")
    assert "\nT0202\n" in result.program_text
    assert result.program_text.endswith("M05\nM30\n%")


def test_rejects_direct_rpm_above_configured_spindle_limit() -> None:
    with pytest.raises(
        GCodeFormattingError,
        match="SPINDLE_SPEED_EXCEEDS_CONFIGURED_MACHINE_LIMIT",
    ):
        format_gcode_candidate(
            _request(
                spindle_mode=SpindleMode.G97_DIRECT_RPM,
                spindle_value=4_000.0,
                max_spindle_rpm=3_000.0,
            )
        )


def test_rejects_effective_feed_above_configured_machine_limit() -> None:
    with pytest.raises(GCodeFormattingError, match="FEED_EXCEEDS_CONFIGURED_MACHINE_LIMIT"):
        format_gcode_candidate(
            _request(
                feed_mode=FeedMode.G95_PER_REVOLUTION,
                feed_value=20.0,
                spindle_value=1_000.0,
                max_feed_mm_min=10_000.0,
            )
        )


def test_rejects_tool_name_that_could_inject_controller_blocks() -> None:
    with pytest.raises(ValidationError, match="tool_name"):
        _request(tool_name='FERRAMENTA"\nM30')
