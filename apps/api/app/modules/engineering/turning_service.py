"""Internal synthetic CAD/CAM orchestration; no endpoint or physical authority."""

from __future__ import annotations

import hashlib
import io
import json
import math
from datetime import datetime
from importlib.metadata import version
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.cad.profile_extractor import TurningDatum, extract_turning_profile
from app.modules.engineering.turning_planner import (
    SyntheticTurningPlanningError, generate_turning_roughing_plan,
)
from app.modules.engineering.turning_schemas import TurningStockCylinder
from app.modules.engineering.turning_toolpath_schemas import (
    SyntheticTurningExecutionResult, SyntheticTurningMetadata, SyntheticTurningParameters,
    TurningChuckFixture, TurningStaticExclusionZone, TurningToolEnvelope2D, UtcTimestamp,
)
from app.modules.engineering.turning_verifier import verify_toolpath_boundaries


class _Inputs(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False,
                              revalidate_instances="always")
    # Nonfinite scale is classified as a CAD failure, never silently normalized to null.
    brep_unit_scale: float = Field(allow_inf_nan=True)
    linear_tolerance_mm: float = Field(gt=0)
    angular_tolerance_rad: float = Field(gt=0)
    datum: TurningDatum
    stock: TurningStockCylinder
    params: SyntheticTurningParameters
    fixture: TurningChuckFixture
    tool_envelope: TurningToolEnvelope2D
    exclusion_zones: tuple[TurningStaticExclusionZone, ...] = Field(max_length=128)
    evaluated_at_utc: UtcTimestamp


def _parameter_digest(inputs: _Inputs) -> str:
    data = inputs.model_dump(mode="json", exclude={"brep_unit_scale"})
    scale = inputs.brep_unit_scale
    data["brep_unit_scale"] = scale if math.isfinite(scale) else {
        "non_finite": "NaN" if math.isnan(scale) else ("+Infinity" if scale > 0 else "-Infinity"),
    }
    data["schema_version"] = "synthetic-turning/v1"
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _copy_and_serialize(shape: Any) -> tuple[Any, str, str]:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy  # type: ignore[import-untyped]
    from OCP.BRepTools import BRepTools  # type: ignore[import-untyped]
    from OCP.TopAbs import TopAbs_FACE  # type: ignore[import-untyped]
    from OCP.TopExp import TopExp_Explorer  # type: ignore[import-untyped]
    from OCP.TopTools import TopTools_FormatVersion  # type: ignore[import-untyped]

    if shape.IsNull():
        raise ValueError("NULL_BREP")
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    count = 0
    while explorer.More():
        count += 1
        if count > 512:
            raise ValueError("BREP_FACE_LIMIT")
        explorer.Next()
    copied = BRepBuilderAPI_Copy(shape).Shape()
    output = io.BytesIO()
    BRepTools.Write_s(copied, output, False, False,
                     TopTools_FormatVersion.TopTools_FormatVersion_VERSION_3)
    data = output.getvalue()
    if not data or len(data) > 20_000_000:
        raise ValueError("BREP_SERIALIZATION_SIZE")
    return copied, hashlib.sha256(data).hexdigest(), version("cadquery-ocp")


def orchestrate_synthetic_turning_pipeline(
    step_brep_solid: Any,
    brep_unit_scale: float,
    linear_tolerance_mm: float,
    angular_tolerance_rad: float,
    datum: TurningDatum,
    stock: TurningStockCylinder,
    params: SyntheticTurningParameters,
    fixture: TurningChuckFixture,
    tool_envelope: TurningToolEnvelope2D,
    exclusion_zones: tuple[TurningStaticExclusionZone, ...],
    evaluated_at_utc: datetime,
) -> SyntheticTurningExecutionResult:
    """Same inputs/time/binding yield the same local synthetic result.

    Invalid typed contracts raise; invalid scale is a structured CAD failure.
    Native BRep serialization is version-specific, not a canonical geometry or
    source STEP identity. No clock, network, persistence or caller digest is used.
    """
    inputs = _Inputs(
        brep_unit_scale=brep_unit_scale, linear_tolerance_mm=linear_tolerance_mm,
        angular_tolerance_rad=angular_tolerance_rad,
        datum=TurningDatum.model_validate(datum.model_dump()), stock=stock, params=params,
        fixture=fixture, tool_envelope=tool_envelope, exclusion_zones=exclusion_zones,
        evaluated_at_utc=evaluated_at_utc,
    )
    if len({zone.zone_id for zone in inputs.exclusion_zones}) != len(inputs.exclusion_zones):
        raise ValueError("declared zone ids must be unique")
    metadata = SyntheticTurningMetadata(
        evaluated_at_utc=inputs.evaluated_at_utc, parameters_digest_sha256=_parameter_digest(inputs),
        brep_serialization_digest_sha256=None, brep_serialization_format=None,
    )
    unit = {1.0: "mm", 1000.0: "m", 25.4: "in"}.get(inputs.brep_unit_scale)
    if unit is None:
        return SyntheticTurningExecutionResult(
            pipeline_status="CAD_EXTRACTION_FAILED", failure_reason="UNSUPPORTED_BREP_UNIT_SCALE",
            profile=None, plan=None, verification=None, metadata=metadata,
        )
    try:
        copied, digest, binding = _copy_and_serialize(step_brep_solid)
    except Exception:
        # Isolate the untyped native boundary; never reflect native details or fabricate a hash.
        return SyntheticTurningExecutionResult(
            pipeline_status="CAD_EXTRACTION_FAILED", failure_reason="BREP_SERIALIZATION_FAILED",
            profile=None, plan=None, verification=None, metadata=metadata,
        )
    metadata = SyntheticTurningMetadata(
        evaluated_at_utc=inputs.evaluated_at_utc, parameters_digest_sha256=metadata.parameters_digest_sha256,
        brep_serialization_digest_sha256=digest,
        brep_serialization_format="OCCT_BREP_ASCII_V3_NO_TRIANGLES_NO_NORMALS",
        occt_binding_version=binding,
    )
    try:
        extraction = extract_turning_profile(
            copied, datum=inputs.datum, source_unit=unit,
            linear_tolerance_mm=inputs.linear_tolerance_mm,
            angular_tolerance_rad=inputs.angular_tolerance_rad,
        )
    except Exception:
        return SyntheticTurningExecutionResult(
            pipeline_status="CAD_EXTRACTION_FAILED", failure_reason="CAD_EXTRACTION_EXCEPTION",
            profile=None, plan=None, verification=None, metadata=metadata,
        )
    if extraction.status != "PROFILE_AVAILABLE_REQUIRES_REVIEW" or extraction.profile is None:
        return SyntheticTurningExecutionResult(
            pipeline_status="CAD_EXTRACTION_FAILED",
            failure_reason=extraction.reasons[0] if extraction.reasons else "CAD_EXTRACTION_REJECTED",
            profile=None, plan=None, verification=None, metadata=metadata,
        )
    profile = extraction.profile
    try:
        plan = generate_turning_roughing_plan(profile, inputs.stock, inputs.params)
    except SyntheticTurningPlanningError as exc:
        return SyntheticTurningExecutionResult(
            pipeline_status="PLANNING_FAILED", failure_reason=str(exc), profile=profile,
            plan=None, verification=None, metadata=metadata,
        )
    except Exception:
        return SyntheticTurningExecutionResult(
            pipeline_status="PLANNING_FAILED", failure_reason="PLANNING_EXCEPTION", profile=profile,
            plan=None, verification=None, metadata=metadata,
        )
    try:
        verification = verify_toolpath_boundaries(
            plan, inputs.fixture, inputs.tool_envelope, inputs.exclusion_zones,
        )
    except Exception:
        return SyntheticTurningExecutionResult(
            pipeline_status="BOUNDARY_VERIFICATION_FAILED", failure_reason="BOUNDARY_VERIFICATION_EXCEPTION",
            profile=profile, plan=plan, verification=None, metadata=metadata,
        )
    success = verification.declared_boundaries_passed and verification.boundary_status == "PASS"
    return SyntheticTurningExecutionResult(
        pipeline_status="SUCCESS_SYNTHETIC" if success else "BOUNDARY_VERIFICATION_FAILED",
        failure_reason=None if success else verification.boundary_status,
        profile=profile, plan=plan, verification=verification, metadata=metadata,
    )
