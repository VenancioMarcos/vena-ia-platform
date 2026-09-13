from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import MachiningPass, RzPoint, TurningStrategyPlanResponse
from app.modules.cnc.enums import CNCControllerType
from app.modules.cnc.schemas import GCodeGenerationRequest
from app.modules.cnc.services.gcode_formatter import format_gcode_candidate


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
