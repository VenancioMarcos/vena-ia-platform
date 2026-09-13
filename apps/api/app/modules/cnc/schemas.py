import math
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import TurningBoundingBox, TurningStrategyPlanResponse
from app.modules.cnc.enums import CNCControllerType, FeedMode, ProgramSafetyLevel, SpindleMode


class CNCOperationType(StrEnum):
    FACE_MILLING = "FACE_MILLING"
    CONTOUR_MILLING = "CONTOUR_MILLING"
    DRILLING = "DRILLING"


class CNCPlanRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")

    operation: CNCOperationType
    tool_number: int = Field(ge=1, le=999)
    spindle_rpm: float = Field(gt=0, le=30_000)
    feed_mm_min: float = Field(gt=0, le=30_000)
    clearance_z_mm: float = Field(gt=0, le=1_000)


class CNCPlanPreview(BaseModel):
    schema_version: str = "vena-ia.cnc-neutral-plan/v1"
    source_planning_reference: str | None = None
    source_recommendation_reference: str | None = None
    controller_family: str
    machine_profile: str
    operation: CNCOperationType
    parameters: dict[str, float | int]
    operation_candidates: list[dict[str, object]] = Field(default_factory=list)
    machine_neutral_assumptions: list[str] = Field(default_factory=list)
    validation_checks: list[str]
    status: str
    warnings: list[str] = Field(default_factory=list)
    traceability: list[str] = Field(default_factory=list)
    review_status: Literal["REQUIRES_HUMAN_REVIEW"] = "REQUIRES_HUMAN_REVIEW"
    simulation_only: Literal[True] = True
    executable_output: Literal[False] = False
    limitations: list[str]


class _CNCGenerationContract(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
        revalidate_instances="always",
        str_strip_whitespace=True,
    )


class GCodeSafetyFlags(_CNCGenerationContract):
    physical_use_authorized: Literal[False] = False
    g9: Literal["PENDING_AUTHORITATIVE_REVIEW"] = "PENDING_AUTHORITATIVE_REVIEW"
    no_human_review_bypass: Literal[True] = True
    machine_send: Literal[False] = False
    dnc: Literal[False] = False
    nc_transfer: Literal[False] = False
    cycle_start: Literal[False] = False
    emission_status: Literal["CONTROLLER_PROFILE_UNRESOLVED"] = "CONTROLLER_PROFILE_UNRESOLVED"
    executable_output: Literal[False] = False


class GCodeGenerationMetadata(_CNCGenerationContract):
    path_length_mm: float = Field(ge=0)
    estimated_cycle_time_seconds: float = Field(ge=0)
    motion_block_count: int = Field(ge=1)
    coordinate_convention: Literal["LATHE_X_DIAMETER_Z"] = "LATHE_X_DIAMETER_Z"


class ChuckExclusionZone2D(_CNCGenerationContract):
    x_min_mm: float
    x_max_mm: float
    z_min_mm: float
    z_max_mm: float

    @model_validator(mode="after")
    def validate_bounds(self) -> "ChuckExclusionZone2D":
        if self.x_min_mm >= self.x_max_mm or self.z_min_mm >= self.z_max_mm:
            raise ValueError("CHUCK_EXCLUSION_ZONE_BOUNDS_INVALID")
        return self


class MachineEnvelope2D(_CNCGenerationContract):
    x_min_mm: float
    x_max_mm: float
    z_min_mm: float
    z_max_mm: float
    chuck_exclusion_zone: ChuckExclusionZone2D

    @model_validator(mode="after")
    def validate_bounds(self) -> "MachineEnvelope2D":
        if self.x_min_mm >= self.x_max_mm or self.z_min_mm >= self.z_max_mm:
            raise ValueError("MACHINE_ENVELOPE_BOUNDS_INVALID")
        return self


class GCodeGenerationRequest(_CNCGenerationContract):
    plan_id: str = Field(min_length=1, max_length=255)
    cam_plan_data: TurningStrategyPlanResponse
    controller_profile: CNCControllerType = Field(strict=False)
    program_number: int = Field(ge=1, le=99_999_999)
    machine_envelope: MachineEnvelope2D
    review_authentication: Literal["AUTHENTICATED_REVIEW_CONTEXT"]
    feed_mode: FeedMode = Field(default=FeedMode.G95_PER_REVOLUTION, strict=False)
    spindle_mode: SpindleMode = Field(default=SpindleMode.G97_DIRECT_RPM, strict=False)
    feed_value: float = Field(default=0.2, gt=0, le=30_000)
    spindle_value: float = Field(default=1_000.0, gt=0, le=30_000)
    max_spindle_rpm: float = Field(default=3_000.0, gt=0, le=30_000)
    max_feed_mm_min: float = Field(default=30_000.0, gt=0, le=30_000)
    tool_number: int = Field(default=1, ge=1, le=99)
    tool_offset: int = Field(default=1, ge=1, le=99)
    tool_name: str = Field(
        default="FERRAMENTA",
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9 _-]+$",
    )
    safety_level: Literal[ProgramSafetyLevel.AUDIT_ONLY_NON_EXECUTABLE] = (
        ProgramSafetyLevel.AUDIT_ONLY_NON_EXECUTABLE
    )


class GCodeGenerationResponse(_CNCGenerationContract):
    status: Literal["PLANNED_REQUIRES_REVIEW"] = "PLANNED_REQUIRES_REVIEW"
    plan_id: str
    controller_profile: CNCControllerType
    program_text: str = Field(min_length=1)
    metadata: GCodeGenerationMetadata
    safety_level: Literal[ProgramSafetyLevel.AUDIT_ONLY_NON_EXECUTABLE] = (
        ProgramSafetyLevel.AUDIT_ONLY_NON_EXECUTABLE
    )
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)


class GCodeGatewayRequest(_CNCGenerationContract):
    plan_id: str = Field(min_length=1, max_length=255)
    controller_profile: CNCControllerType = Field(strict=False)
    program_number: int = Field(ge=1, le=99_999_999)
    machine_envelope: MachineEnvelope2D
    max_spindle_rpm: float = Field(default=3_000.0, gt=0, le=30_000)
    max_feed_mm_min: float = Field(default=30_000.0, gt=0, le=30_000)
    tool_number: int = Field(default=1, ge=1, le=99)
    tool_offset: int = Field(default=1, ge=1, le=99)
    tool_name: str = Field(
        default="FERRAMENTA",
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9 _-]+$",
    )


class ToolpathSegment2D(_CNCGenerationContract):
    motion_type: Literal["RAPID", "LINEAR"]
    x_start_mm: float
    z_start_mm: float
    x_end_mm: float
    z_end_mm: float
    feed: float | None = Field(default=None, gt=0)
    effective_feed_mm_min: float | None = Field(default=None, gt=0)
    active_tool: str | None = Field(default=None, min_length=1, max_length=64)


class DimensionalDeviation(_CNCGenerationContract):
    axis: Literal["MAX_RADIUS", "MIN_Z", "MAX_Z"]
    nominal_mm: float
    programmed_mm: float
    signed_deviation_mm: float
    tolerance_mm: float = Field(gt=0, le=1.0)
    within_tolerance: bool

    @model_validator(mode="after")
    def validate_calculation(self) -> "DimensionalDeviation":
        expected = self.programmed_mm - self.nominal_mm
        if not math.isclose(
            self.signed_deviation_mm, expected, abs_tol=1e-12, rel_tol=1e-12
        ):
            raise ValueError("DIMENSIONAL_DEVIATION_INCONSISTENT")
        expected_within = math.isclose(
            self.programmed_mm, self.nominal_mm, abs_tol=self.tolerance_mm, rel_tol=0
        )
        if self.within_tolerance != expected_within:
            raise ValueError("DIMENSIONAL_TOLERANCE_RESULT_INCONSISTENT")
        return self


class GeometryDimensionalAuditReport(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-geometry-dimensional-audit/v1"] = (
        "vena-ia.cnc-geometry-dimensional-audit/v1"
    )
    status: Literal["PASS", "REJECTED"]
    source_brep_bounds: TurningBoundingBox
    programmed_min_radius_mm: float
    programmed_max_radius_mm: float
    programmed_min_z_mm: float
    programmed_max_z_mm: float
    deviations: tuple[DimensionalDeviation, DimensionalDeviation, DimensionalDeviation]
    findings: tuple[str, ...]
    manifest_generation_allowed: bool
    coordinate_convention: Literal["LATHE_X_DIAMETER_Z"] = "LATHE_X_DIAMETER_Z"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_outcome(self) -> "GeometryDimensionalAuditReport":
        passed = not self.findings and all(item.within_tolerance for item in self.deviations)
        if (self.status == "PASS") != passed:
            raise ValueError("GEOMETRY_AUDIT_STATUS_INCONSISTENT")
        if self.manifest_generation_allowed != passed:
            raise ValueError("GEOMETRY_AUDIT_GATE_INCONSISTENT")
        return self


class TurningStock2D(_CNCGenerationContract):
    diameter_mm: float = Field(gt=0)
    z_min_mm: float
    z_max_mm: float

    @model_validator(mode="after")
    def validate_bounds(self) -> "TurningStock2D":
        if self.z_min_mm >= self.z_max_mm:
            raise ValueError("STOCK_Z_BOUNDS_INVALID")
        return self


class ToolpathSimulationRequest(_CNCGenerationContract):
    plan_id: str | None = Field(default=None, min_length=1, max_length=255)
    program_text: str | None = Field(default=None, min_length=1, max_length=1_000_000)
    controller_profile: CNCControllerType = Field(strict=False)
    program_number: int = Field(default=9_000, ge=1, le=99_999_999)
    machine_envelope: MachineEnvelope2D
    stock: TurningStock2D
    max_spindle_rpm: float = Field(default=3_000.0, gt=0, le=30_000)
    max_feed_mm_min: float = Field(default=30_000.0, gt=0, le=30_000)
    tool_number: int = Field(default=1, ge=1, le=99)
    tool_offset: int = Field(default=1, ge=1, le=99)
    tool_name: str = Field(
        default="FERRAMENTA",
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9 _-]+$",
    )

    @model_validator(mode="after")
    def validate_source(self) -> "ToolpathSimulationRequest":
        if (self.plan_id is None) == (self.program_text is None):
            raise ValueError("EXACTLY_ONE_SIMULATION_SOURCE_REQUIRED")
        return self


class ChuckProximityAudit(_CNCGenerationContract):
    minimum_clearance_mm: float = Field(ge=0)
    threshold_mm: float = Field(default=5.0, gt=0)
    closest_segment_index: int = Field(ge=0)
    warning_code: Literal["WARNING_PROXIMITY_CHUCK"] | None = None


class CycleTimeToolBreakdown(_CNCGenerationContract):
    tool: str
    cutting_time_seconds: float = Field(ge=0)
    rapid_time_seconds: float = Field(ge=0)
    cutting_distance_mm: float = Field(ge=0)
    rapid_distance_mm: float = Field(ge=0)


class CycleTimeEstimatePayload(_CNCGenerationContract):
    total_cutting_time_seconds: float = Field(ge=0)
    total_rapid_time_seconds: float = Field(ge=0)
    total_cycle_time_seconds: float = Field(ge=0)
    total_cutting_distance_mm: float = Field(ge=0)
    total_rapid_distance_mm: float = Field(ge=0)
    rapid_feed_rate_mm_min: float = Field(gt=0)
    per_tool_breakdown: tuple[CycleTimeToolBreakdown, ...]
    disclaimer: Literal["THEORETICAL_ANALYTICAL_ESTIMATE_NOT_PHYSICALLY_APPROVED"] = (
        "THEORETICAL_ANALYTICAL_ESTIMATE_NOT_PHYSICALLY_APPROVED"
    )


class ToolpathSimulationPayload(_CNCGenerationContract):
    status: Literal["SIMULATION_READY_REQUIRES_REVIEW"] = "SIMULATION_READY_REQUIRES_REVIEW"
    source_plan_id: str | None = None
    controller_profile: CNCControllerType
    segments: tuple[ToolpathSegment2D, ...] = Field(min_length=1)
    machine_envelope: MachineEnvelope2D
    stock: TurningStock2D
    chuck_proximity: ChuckProximityAudit
    cycle_time_estimate: CycleTimeEstimatePayload | None = None
    coordinate_convention: Literal["LATHE_X_DIAMETER_Z"] = "LATHE_X_DIAMETER_Z"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)


class MachiningReportTool(_CNCGenerationContract):
    tool_id: str = Field(min_length=1)
    operations: tuple[TurningOperationType, ...] = Field(min_length=1)


class SurfaceRoughnessAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-surface-roughness-audit/v1"] = (
        "vena-ia.cnc-surface-roughness-audit/v1"
    )
    ra_theoretical_um: float = Field(gt=0)
    rz_theoretical_um: float = Field(gt=0)
    finish_feed_mm_per_rev: float = Field(gt=0, le=5.0)
    insert_nose_radius_mm: float = Field(gt=0, le=10.0)
    nominal_ra_max_um: float | None = Field(default=None, gt=0, le=1_000)
    compliance_tag: Literal[
        "WITHIN_NOMINAL_RA_TOLERANCE",
        "EXCEEDS_NOMINAL_RA_TOLERANCE",
        "NOMINAL_RA_TOLERANCE_UNAVAILABLE",
    ]
    model_limitation: Literal[
        "IDEAL_KINEMATIC_MODEL_EXCLUDES_VIBRATION_TOOL_WEAR_AND_MATERIAL_EFFECTS"
    ] = "IDEAL_KINEMATIC_MODEL_EXCLUDES_VIBRATION_TOOL_WEAR_AND_MATERIAL_EFFECTS"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_ideal_model(self) -> "SurfaceRoughnessAuditPayload":
        expected_ra = (
            self.finish_feed_mm_per_rev**2 / (32 * self.insert_nose_radius_mm) * 1_000
        )
        expected_rz = (
            self.finish_feed_mm_per_rev**2 / (8 * self.insert_nose_radius_mm) * 1_000
        )
        if not math.isclose(self.ra_theoretical_um, expected_ra, abs_tol=5e-9, rel_tol=1e-12):
            raise ValueError("SURFACE_ROUGHNESS_RA_INCONSISTENT")
        if not math.isclose(self.rz_theoretical_um, expected_rz, abs_tol=5e-9, rel_tol=1e-12):
            raise ValueError("SURFACE_ROUGHNESS_RZ_INCONSISTENT")
        expected_tag = (
            "NOMINAL_RA_TOLERANCE_UNAVAILABLE"
            if self.nominal_ra_max_um is None
            else (
                "WITHIN_NOMINAL_RA_TOLERANCE"
                if self.ra_theoretical_um <= self.nominal_ra_max_um
                else "EXCEEDS_NOMINAL_RA_TOLERANCE"
            )
        )
        if self.compliance_tag != expected_tag:
            raise ValueError("SURFACE_ROUGHNESS_COMPLIANCE_INCONSISTENT")
        return self


class MachiningPowerForceAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-power-force-audit/v1"] = (
        "vena-ia.cnc-machining-power-force-audit/v1"
    )
    material_profile: Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
    kc1_1_n_per_mm2: float = Field(gt=0)
    kienzle_exponent_mc: float = Field(gt=0, lt=1)
    feed_mm_per_rev: float = Field(gt=0, le=5.0)
    depth_of_cut_mm: float = Field(gt=0, le=100.0)
    cutting_edge_angle_deg: float = Field(gt=0, le=179.0)
    chip_thickness_mm: float = Field(gt=0)
    chip_width_mm: float = Field(gt=0)
    cutting_speed_m_per_min: float = Field(gt=0, le=3_000.0)
    spindle_rpm_reference: float = Field(gt=0, le=30_000.0)
    max_spindle_rpm: float = Field(gt=0, le=30_000.0)
    fc_nominal_n: float = Field(gt=0)
    pc_cutting_kw: float = Field(gt=0)
    p_motor_est_kw: float = Field(gt=0)
    mrr_cm3_min: float = Field(gt=0)
    machine_power_limit_kw: float = Field(gt=0, le=1_000.0)
    power_status: Literal["POWER_WITHIN_LIMITS", "POWER_EXCEEDED_WARNING"]
    spindle_efficiency: float = Field(default=0.80, ge=0.80, le=0.80)
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "KIENZLE_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_DYNAMIC_EFFICIENCY"
    ] = "KIENZLE_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_DYNAMIC_EFFICIENCY"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_analytical_model(self) -> "MachiningPowerForceAuditPayload":
        expected_material = {
            "AISI_1020": (1_780.0, 0.25),
            "ABNT_1045": (1_900.0, 0.26),
            "ALUMINUM_6061_T6": (700.0, 0.23),
        }[self.material_profile]
        if (self.kc1_1_n_per_mm2, self.kienzle_exponent_mc) != expected_material:
            raise ValueError("KIENZLE_MATERIAL_PARAMETERS_INCONSISTENT")
        if self.spindle_rpm_reference > self.max_spindle_rpm:
            raise ValueError("KIENZLE_SPINDLE_RPM_EXCEEDS_LIMIT")
        sin_kr = math.sin(math.radians(self.cutting_edge_angle_deg))
        expected_width = self.depth_of_cut_mm / sin_kr
        expected_thickness = self.feed_mm_per_rev * sin_kr
        expected_force = (
            self.kc1_1_n_per_mm2
            * expected_width
            * expected_thickness ** (1 - self.kienzle_exponent_mc)
        )
        expected_cutting_power = (
            expected_force * self.cutting_speed_m_per_min / (60 * 1_000)
        )
        expected_motor_power = expected_cutting_power / self.spindle_efficiency
        expected_mrr = (
            self.cutting_speed_m_per_min * self.depth_of_cut_mm * self.feed_mm_per_rev
        )
        checks = (
            (self.chip_width_mm, expected_width, "KIENZLE_CHIP_WIDTH_INCONSISTENT"),
            (self.chip_thickness_mm, expected_thickness, "KIENZLE_CHIP_THICKNESS_INCONSISTENT"),
            (self.fc_nominal_n, expected_force, "KIENZLE_FORCE_INCONSISTENT"),
            (self.pc_cutting_kw, expected_cutting_power, "KIENZLE_CUTTING_POWER_INCONSISTENT"),
            (self.p_motor_est_kw, expected_motor_power, "KIENZLE_MOTOR_POWER_INCONSISTENT"),
            (self.mrr_cm3_min, expected_mrr, "KIENZLE_MRR_INCONSISTENT"),
        )
        for actual, expected, code in checks:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "POWER_WITHIN_LIMITS"
            if self.p_motor_est_kw <= self.machine_power_limit_kw
            else "POWER_EXCEEDED_WARNING"
        )
        if self.power_status != expected_status:
            raise ValueError("KIENZLE_POWER_STATUS_INCONSISTENT")
        return self


class MachiningTechnicalReportPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-report/v1"] = "vena-ia.cnc-machining-report/v1"
    status: Literal["REQUIRES_HUMAN_REVIEW"] = "REQUIRES_HUMAN_REVIEW"
    plan_id: str = Field(min_length=1)
    source_plan_name: None = None
    cad_job_id: str = Field(min_length=1)
    controller_profile: CNCControllerType
    program_number: int = Field(ge=1)
    program_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    analytical_snapshot_at: datetime
    tools: tuple[MachiningReportTool, ...] = Field(min_length=1)
    cycle_time_estimate: CycleTimeEstimatePayload
    total_distance_mm: float = Field(ge=0)
    envelope_audit: Literal["PASS_DECLARED_2D_ENVELOPE_ONLY"]
    machine_envelope: MachineEnvelope2D
    chuck_proximity: ChuckProximityAudit
    geometry_audit: GeometryDimensionalAuditReport
    surface_roughness_audit: SurfaceRoughnessAuditPayload
    power_force_audit: MachiningPowerForceAuditPayload
    coordinate_convention: Literal["LATHE_X_DIAMETER_Z"] = "LATHE_X_DIAMETER_Z"
    governance_stamp: Literal["RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO"] = (
        "RELATÓRIO PURAMENTE ANALÍTICO - USO FÍSICO NÃO AUTORIZADO"
    )
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_snapshot_time(self) -> "MachiningTechnicalReportPayload":
        if self.analytical_snapshot_at.tzinfo is None:
            raise ValueError("REPORT_TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
        return self
