import math
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.cam.enums import TurningOperationType
from app.modules.cam.schemas import RzPoint, TurningBoundingBox, TurningStrategyPlanResponse
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


class ToolLifeTaylorAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-tool-life-taylor-audit/v1"] = (
        "vena-ia.cnc-tool-life-taylor-audit/v1"
    )
    tool_id: str = Field(min_length=1, max_length=64)
    tool_material_pair: Literal[
        "CARBIDE_P20_P30_CARBON_STEEL", "CARBIDE_K10_ALUMINUM_6061_T6"
    ]
    cutting_speed_vc_m_per_min: float = Field(gt=0)
    taylor_n: float = Field(gt=0, lt=1)
    taylor_c: float = Field(gt=0)
    effective_cutting_time_minutes: float = Field(ge=0)
    estimated_tool_life_minutes: float = Field(gt=0)
    tool_life_consumed_percent: float = Field(ge=0)
    integrity_status: Literal["TOOL_LIFE_SAFE", "TOOL_LIFE_EXHAUSTED_WARNING"]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "TAYLOR_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_THERMAL_AND_LUBRICATION_VARIATION"
    ] = "TAYLOR_ANALYTICAL_ESTIMATE_EXCLUDES_REAL_THERMAL_AND_LUBRICATION_VARIATION"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_taylor_model(self) -> "ToolLifeTaylorAuditPayload":
        expected_profile_parameters = {
            "CARBIDE_P20_P30_CARBON_STEEL": (0.25, 350.0),
            "CARBIDE_K10_ALUMINUM_6061_T6": (0.30, 800.0),
        }[self.tool_material_pair]
        if (self.taylor_n, self.taylor_c) != expected_profile_parameters:
            raise ValueError("TAYLOR_PROFILE_PARAMETERS_INCONSISTENT")
        expected_life = (self.taylor_c / self.cutting_speed_vc_m_per_min) ** (
            1 / self.taylor_n
        )
        expected_consumed = self.effective_cutting_time_minutes / expected_life * 100
        if not math.isclose(
            self.estimated_tool_life_minutes, expected_life, abs_tol=5e-9, rel_tol=1e-12
        ):
            raise ValueError("TAYLOR_TOOL_LIFE_INCONSISTENT")
        if not math.isclose(
            self.tool_life_consumed_percent,
            expected_consumed,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("TAYLOR_CONSUMPTION_INCONSISTENT")
        expected_status = (
            "TOOL_LIFE_SAFE"
            if self.tool_life_consumed_percent <= 80
            else "TOOL_LIFE_EXHAUSTED_WARNING"
        )
        if self.integrity_status != expected_status:
            raise ValueError("TAYLOR_STATUS_INCONSISTENT")
        return self


class ToolingWearCostComponent(_CNCGenerationContract):
    tool_id: str = Field(min_length=1, max_length=64)
    effective_cutting_time_minutes: float = Field(ge=0)
    estimated_tool_life_minutes: float = Field(gt=0)
    consumed_fraction: float = Field(ge=0)
    cutting_edge_cost: float = Field(ge=0)
    estimated_wear_cost: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_wear_cost(self) -> "ToolingWearCostComponent":
        expected_fraction = self.effective_cutting_time_minutes / self.estimated_tool_life_minutes
        expected_cost = expected_fraction * self.cutting_edge_cost
        if not math.isclose(self.consumed_fraction, expected_fraction, abs_tol=5e-9):
            raise ValueError("TOOLING_WEAR_FRACTION_INCONSISTENT")
        if not math.isclose(self.estimated_wear_cost, expected_cost, abs_tol=5e-9):
            raise ValueError("TOOLING_WEAR_COST_INCONSISTENT")
        return self


class MachiningCostTimeAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-cost-time-audit/v1"] = (
        "vena-ia.cnc-machining-cost-time-audit/v1"
    )
    cost_profile: Literal["BRL_STANDARD", "USD_STANDARD"]
    total_cycle_time_minutes: float = Field(ge=0)
    cutting_time_minutes: float = Field(ge=0)
    rapid_time_minutes: float = Field(ge=0)
    tool_change_count: int = Field(ge=0)
    tool_change_time_minutes_each: float = Field(ge=0)
    tool_change_time_minutes: float = Field(ge=0)
    setup_count: int = Field(ge=0)
    nominal_setup_time_minutes_each: float = Field(ge=0)
    nominal_setup_time_minutes: float = Field(ge=0)
    estimated_total_cost: float = Field(ge=0)
    machine_cost_component: float = Field(ge=0)
    tooling_wear_cost_component: float = Field(ge=0)
    machine_hourly_rate: float = Field(ge=0)
    cutting_edge_cost: float = Field(ge=0)
    currency: Literal["BRL", "USD"]
    per_tool_wear_costs: tuple[ToolingWearCostComponent, ...] = Field(min_length=1)
    is_theoretical_estimate: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_COST_TIME_EXCLUDES_LOGISTICS_UNPLANNED_DOWNTIME_AND_TAXES"
    ] = "ANALYTICAL_COST_TIME_EXCLUDES_LOGISTICS_UNPLANNED_DOWNTIME_AND_TAXES"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_cost_time_model(self) -> "MachiningCostTimeAuditPayload":
        expected_profile = {
            "BRL_STANDARD": ("BRL", 120.0, 15.0),
            "USD_STANDARD": ("USD", 25.0, 3.0),
        }[self.cost_profile]
        if (self.currency, self.machine_hourly_rate, self.cutting_edge_cost) != expected_profile:
            raise ValueError("COST_TIME_PROFILE_PARAMETERS_INCONSISTENT")
        expected_change = self.tool_change_count * self.tool_change_time_minutes_each
        expected_setup = self.setup_count * self.nominal_setup_time_minutes_each
        expected_total_time = (
            self.cutting_time_minutes
            + self.rapid_time_minutes
            + expected_change
            + expected_setup
        )
        expected_tooling = math.fsum(item.estimated_wear_cost for item in self.per_tool_wear_costs)
        expected_machine = expected_total_time / 60 * self.machine_hourly_rate
        comparisons = (
            (self.tool_change_time_minutes, expected_change, "TOOL_CHANGE_TIME_INCONSISTENT"),
            (self.nominal_setup_time_minutes, expected_setup, "SETUP_TIME_INCONSISTENT"),
            (self.total_cycle_time_minutes, expected_total_time, "TOTAL_CYCLE_TIME_INCONSISTENT"),
            (self.machine_cost_component, expected_machine, "MACHINE_COST_INCONSISTENT"),
            (self.tooling_wear_cost_component, expected_tooling, "TOOLING_COST_INCONSISTENT"),
            (
                self.estimated_total_cost,
                expected_machine + expected_tooling,
                "TOTAL_COST_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9):
                raise ValueError(code)
        return self


class MachiningSustainabilityAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-sustainability-audit/v1"] = (
        "vena-ia.cnc-machining-sustainability-audit/v1"
    )
    electrical_energy_kwh: float = Field(ge=0)
    cutting_energy_kwh: float = Field(ge=0)
    standby_energy_kwh: float = Field(ge=0)
    carbon_emission_kg_co2e: float = Field(ge=0)
    grid_region: Literal["BRASIL_SIN", "USA_AVG", "EU_AVG"]
    grid_emission_factor_kg_co2e_per_kwh: float = Field(gt=0)
    motor_power_kw: float = Field(gt=0)
    standby_power_kw: float = Field(gt=0)
    cutting_time_minutes: float = Field(ge=0)
    total_cycle_time_minutes: float = Field(ge=0)
    electrical_efficiency: float = Field(gt=0, le=1)
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_ENERGY_CARBON_EXCLUDES_EXTERNAL_COOLING_AND_STARTUP_PEAKS"
    ] = "ANALYTICAL_ENERGY_CARBON_EXCLUDES_EXTERNAL_COOLING_AND_STARTUP_PEAKS"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_sustainability_model(self) -> "MachiningSustainabilityAuditPayload":
        expected_factor = {
            "BRASIL_SIN": 0.085,
            "USA_AVG": 0.385,
            "EU_AVG": 0.230,
        }[self.grid_region]
        if self.grid_emission_factor_kg_co2e_per_kwh != expected_factor:
            raise ValueError("SUSTAINABILITY_GRID_FACTOR_INCONSISTENT")
        if self.total_cycle_time_minutes < self.cutting_time_minutes:
            raise ValueError("SUSTAINABILITY_TIME_DECOMPOSITION_INVALID")
        expected_cutting = (
            self.motor_power_kw * self.cutting_time_minutes / 60 / self.electrical_efficiency
        )
        expected_standby = (
            self.standby_power_kw
            * (self.total_cycle_time_minutes - self.cutting_time_minutes)
            / 60
            / self.electrical_efficiency
        )
        expected_total = expected_cutting + expected_standby
        comparisons = (
            (self.cutting_energy_kwh, expected_cutting, "CUTTING_ENERGY_INCONSISTENT"),
            (self.standby_energy_kwh, expected_standby, "STANDBY_ENERGY_INCONSISTENT"),
            (self.electrical_energy_kwh, expected_total, "TOTAL_ENERGY_INCONSISTENT"),
            (
                self.carbon_emission_kg_co2e,
                expected_total * expected_factor,
                "CARBON_EMISSION_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9):
                raise ValueError(code)
        return self


class MachiningStabilityAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-stability-audit/v1"] = (
        "vena-ia.cnc-machining-stability-audit/v1"
    )
    tool_id: str = Field(min_length=1, max_length=64)
    tool_overhang_mm: float = Field(gt=0)
    tool_diameter_mm: float = Field(gt=0)
    overhang_ratio_l_d: float = Field(gt=0)
    young_modulus_mpa: float = Field(gt=0)
    second_moment_area_mm4: float = Field(gt=0)
    equivalent_stiffness_n_per_mm: float = Field(gt=0)
    cutting_force_n: float = Field(gt=0)
    static_deflection_um: float = Field(gt=0)
    specific_cutting_pressure_n_per_mm2: float = Field(gt=0)
    frf_real_compliance_mm_per_n: float = Field(gt=0)
    depth_of_cut_mm: float = Field(gt=0)
    stability_limit_depth_mm: float = Field(gt=0)
    stability_status: Literal["DYNAMICALLY_STABLE", "CHATTER_HIGH_RISK_WARNING"]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_STABILITY_EXCLUDES_WORKPIECE_AND_SPINDLE_VIBRATION_MODES"
    ] = "ANALYTICAL_STABILITY_EXCLUDES_WORKPIECE_AND_SPINDLE_VIBRATION_MODES"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_stability_model(self) -> "MachiningStabilityAuditPayload":
        expected_ratio = self.tool_overhang_mm / self.tool_diameter_mm
        expected_inertia = math.pi * self.tool_diameter_mm**4 / 64
        expected_stiffness = (
            3 * self.young_modulus_mpa * expected_inertia / self.tool_overhang_mm**3
        )
        expected_deflection = self.cutting_force_n / expected_stiffness * 1_000
        expected_limit = 1 / (
            2
            * self.specific_cutting_pressure_n_per_mm2
            * self.frf_real_compliance_mm_per_n
        )
        comparisons = (
            (self.overhang_ratio_l_d, expected_ratio, "STABILITY_OVERHANG_RATIO_INCONSISTENT"),
            (self.second_moment_area_mm4, expected_inertia, "STABILITY_INERTIA_INCONSISTENT"),
            (
                self.equivalent_stiffness_n_per_mm,
                expected_stiffness,
                "STABILITY_STIFFNESS_INCONSISTENT",
            ),
            (self.static_deflection_um, expected_deflection, "STABILITY_DEFLECTION_INCONSISTENT"),
            (
                self.stability_limit_depth_mm,
                expected_limit,
                "STABILITY_LIMIT_DEPTH_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "DYNAMICALLY_STABLE"
            if self.overhang_ratio_l_d <= 4 and self.depth_of_cut_mm <= self.stability_limit_depth_mm
            else "CHATTER_HIGH_RISK_WARNING"
        )
        if self.stability_status != expected_status:
            raise ValueError("STABILITY_STATUS_INCONSISTENT")
        return self


class MachiningParameterOptimizationPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-parameter-optimization/v1"] = (
        "vena-ia.cnc-machining-parameter-optimization/v1"
    )
    tool_id: str = Field(min_length=1, max_length=64)
    material_profile: Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
    programmed_vc_m_min: float = Field(gt=0)
    programmed_feed_mm_rev: float = Field(gt=0)
    programmed_ap_mm: float = Field(gt=0)
    vc_min_m_min: float = Field(gt=0)
    vc_max_m_min: float = Field(gt=0)
    feed_min_mm_rev: float = Field(gt=0)
    feed_max_mm_rev: float = Field(gt=0)
    ap_min_mm: float = Field(gt=0)
    ap_max_mm: float = Field(gt=0)
    target_ra_um: float = Field(gt=0)
    insert_nose_radius_mm: float = Field(gt=0)
    cutting_edge_angle_deg: float = Field(gt=0, lt=180)
    machine_power_limit_kw: float = Field(gt=0)
    stability_limit_depth_mm: float = Field(gt=0)
    overhang_ratio_l_d: float = Field(gt=0)
    recommended_vc_m_min: float | None = Field(default=None, gt=0)
    recommended_feed_mm_rev: float | None = Field(default=None, gt=0)
    recommended_ap_mm: float | None = Field(default=None, gt=0)
    predicted_mrr_cm3_min: float | None = Field(default=None, gt=0)
    predicted_motor_power_kw: float | None = Field(default=None, gt=0)
    predicted_ra_um: float | None = Field(default=None, gt=0)
    predicted_tool_life_minutes: float | None = Field(default=None, gt=0)
    optimization_status: Literal[
        "OPTIMAL_TRADE_OFF_FOUND", "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED"
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_CUTTING_PARAMETERS_REQUIRE_MANUAL_PROCESS_ENGINEERING_APPROVAL"
    ] = "ANALYTICAL_CUTTING_PARAMETERS_REQUIRE_MANUAL_PROCESS_ENGINEERING_APPROVAL"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_optimization_model(self) -> "MachiningParameterOptimizationPayload":
        if not (
            self.vc_min_m_min <= self.programmed_vc_m_min <= self.vc_max_m_min
            and self.feed_min_mm_rev <= self.programmed_feed_mm_rev <= self.feed_max_mm_rev
            and self.ap_min_mm <= self.programmed_ap_mm <= self.ap_max_mm
        ):
            raise ValueError("OPTIMIZATION_PROGRAMMED_PARAMETERS_OUTSIDE_ENVELOPE")
        recommendations = (
            self.recommended_vc_m_min,
            self.recommended_feed_mm_rev,
            self.recommended_ap_mm,
            self.predicted_mrr_cm3_min,
            self.predicted_motor_power_kw,
            self.predicted_ra_um,
            self.predicted_tool_life_minutes,
        )
        kc, mc = {
            "AISI_1020": (1_780.0, 0.25),
            "ABNT_1045": (1_900.0, 0.26),
            "ALUMINUM_6061_T6": (700.0, 0.23),
        }[self.material_profile]
        taylor_n, taylor_c = (
            (0.30, 800.0)
            if self.material_profile == "ALUMINUM_6061_T6"
            else (0.25, 350.0)
        )
        expected_feed = min(
            self.feed_max_mm_rev,
            math.sqrt(self.target_ra_um * 32 * self.insert_nose_radius_mm / 1_000),
        )
        expected_depth = min(self.ap_max_mm, self.stability_limit_depth_mm)
        sin_kr = math.sin(math.radians(self.cutting_edge_angle_deg))
        expected_force_at_unit_speed = (
            kc * (expected_depth / sin_kr) * (expected_feed * sin_kr) ** (1 - mc)
        )
        expected_power_at_unit_speed = expected_force_at_unit_speed / 60_000 / 0.80
        expected_vc = min(
            self.vc_max_m_min, self.machine_power_limit_kw / expected_power_at_unit_speed
        )
        feasible = (
            self.overhang_ratio_l_d <= 4
            and expected_feed >= self.feed_min_mm_rev
            and expected_depth >= self.ap_min_mm
            and expected_vc >= self.vc_min_m_min
        )
        if self.optimization_status == "OPTIMIZATION_UNFEASIBLE_CONSTRAINTS_VIOLATED":
            if any(value is not None for value in recommendations):
                raise ValueError("OPTIMIZATION_UNFEASIBLE_RESULT_MUST_BE_EMPTY")
            if feasible:
                raise ValueError("OPTIMIZATION_FALSE_UNFEASIBLE_STATUS")
            return self
        if not feasible:
            raise ValueError("OPTIMIZATION_FALSE_FEASIBLE_STATUS")
        if any(value is None for value in recommendations):
            raise ValueError("OPTIMIZATION_RECOMMENDATION_REQUIRED")
        assert self.recommended_vc_m_min is not None
        assert self.recommended_feed_mm_rev is not None
        assert self.recommended_ap_mm is not None
        assert self.predicted_mrr_cm3_min is not None
        assert self.predicted_motor_power_kw is not None
        assert self.predicted_ra_um is not None
        assert self.predicted_tool_life_minutes is not None
        vc = self.recommended_vc_m_min
        feed = self.recommended_feed_mm_rev
        depth = self.recommended_ap_mm
        mrr = self.predicted_mrr_cm3_min
        power = self.predicted_motor_power_kw
        roughness = self.predicted_ra_um
        tool_life = self.predicted_tool_life_minutes
        if not (
            self.vc_min_m_min <= vc <= self.vc_max_m_min
            and self.feed_min_mm_rev <= feed <= self.feed_max_mm_rev
            and self.ap_min_mm <= depth <= self.ap_max_mm
            and self.overhang_ratio_l_d <= 4
            and depth <= self.stability_limit_depth_mm
        ):
            raise ValueError("OPTIMIZATION_RECOMMENDATION_OUTSIDE_CONSTRAINTS")
        for actual, expected, code in (
            (vc, expected_vc, "OPTIMIZATION_VC_NOT_OPTIMAL"),
            (feed, expected_feed, "OPTIMIZATION_FEED_NOT_OPTIMAL"),
            (depth, expected_depth, "OPTIMIZATION_AP_NOT_OPTIMAL"),
        ):
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_force = kc * (depth / sin_kr) * (feed * sin_kr) ** (1 - mc)
        expected_power = expected_force * vc / 60_000 / 0.80
        expected_ra = feed**2 / (32 * self.insert_nose_radius_mm) * 1_000
        expected_mrr = vc * feed * depth
        expected_life = (taylor_c / vc) ** (1 / taylor_n)
        checks = (
            (power, expected_power, "OPTIMIZATION_POWER_INCONSISTENT"),
            (roughness, expected_ra, "OPTIMIZATION_ROUGHNESS_INCONSISTENT"),
            (mrr, expected_mrr, "OPTIMIZATION_MRR_INCONSISTENT"),
            (tool_life, expected_life, "OPTIMIZATION_TAYLOR_LIFE_INCONSISTENT"),
        )
        for actual, expected, code in checks:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        if power > self.machine_power_limit_kw or roughness > self.target_ra_um:
            raise ValueError("OPTIMIZATION_RECOMMENDATION_VIOLATES_CONSTRAINT")
        return self


class MachiningRiskMatrixPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-risk-matrix/v1"] = (
        "vena-ia.cnc-machining-risk-matrix/v1"
    )
    envelope_audit: Literal[
        "PASS_DECLARED_2D_ENVELOPE_ONLY", "ENVELOPE_VIOLATION_DETECTED"
    ]
    geometry_audit_status: Literal["PASS", "REJECTED"]
    geometry_manifest_generation_allowed: bool
    minimum_chuck_clearance_mm: float = Field(ge=0)
    chuck_proximity_threshold_mm: float = Field(gt=0)
    chuck_proximity_warning: bool
    max_overhang_ratio_l_d: float = Field(gt=0)
    dynamic_warning_present: bool
    required_motor_power_kw: float = Field(gt=0)
    machine_power_limit_kw: float = Field(gt=0)
    power_warning_present: bool
    max_tool_life_consumed_percent: float = Field(ge=0)
    tool_wear_warning_present: bool
    overall_risk_score: float = Field(ge=0, le=100)
    risk_level: Literal[
        "LOW_RISK",
        "MODERATE_RISK",
        "HIGH_RISK_REQUIRES_MITIGATION",
        "CRITICAL_INTERVENTION_MANDATORY",
    ]
    dimensional_risk_score: float = Field(ge=0, le=100)
    dynamic_risk_score: float = Field(ge=0, le=100)
    energy_risk_score: float = Field(ge=0, le=100)
    tool_wear_risk_score: float = Field(ge=0, le=100)
    mitigation_recommendations: tuple[str, ...] = Field(min_length=1)
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "CONSOLIDATED_ANALYTICAL_RISK_MATRIX_IS_PRELIMINARY_AND_NOT_AN_EXPERT_REPORT"
    ] = "CONSOLIDATED_ANALYTICAL_RISK_MATRIX_IS_PRELIMINARY_AND_NOT_AN_EXPERT_REPORT"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_risk_matrix(self) -> "MachiningRiskMatrixPayload":
        hard_dimensional_violation = (
            self.envelope_audit == "ENVELOPE_VIOLATION_DETECTED"
            or self.geometry_audit_status == "REJECTED"
            or not self.geometry_manifest_generation_allowed
            or self.minimum_chuck_clearance_mm <= 0
        )
        proximity_risk = (
            self.chuck_proximity_warning
            or self.minimum_chuck_clearance_mm < self.chuck_proximity_threshold_mm
        )
        dynamic_risk = self.dynamic_warning_present or self.max_overhang_ratio_l_d > 4
        energy_risk = (
            self.power_warning_present
            or self.required_motor_power_kw > self.machine_power_limit_kw
        )
        wear_risk = (
            self.tool_wear_warning_present
            or self.max_tool_life_consumed_percent > 80
        )
        expected_dimensional = 100.0 if hard_dimensional_violation else 75.0 if proximity_risk else 0.0
        expected_dynamic = 75.0 if dynamic_risk else 0.0
        expected_energy = 75.0 if energy_risk else 0.0
        expected_wear = 75.0 if wear_risk else 0.0
        expected_overall = round(
            expected_dimensional * 0.35
            + expected_dynamic * 0.25
            + expected_energy * 0.20
            + expected_wear * 0.20,
            9,
        )
        expected_level = (
            "CRITICAL_INTERVENTION_MANDATORY"
            if hard_dimensional_violation
            else "HIGH_RISK_REQUIRES_MITIGATION"
            if expected_overall >= 40
            else "MODERATE_RISK"
            if expected_overall >= 15
            else "LOW_RISK"
        )
        expected_recommendations: list[str] = []
        if hard_dimensional_violation:
            expected_recommendations.append(
                "Interromper a avaliação do processo e revisar envelope, geometria e trajetória."
            )
        elif proximity_risk:
            expected_recommendations.append(
                "Revisar trajetória, origem e fixação para ampliar a folga em relação à placa."
            )
        if dynamic_risk:
            expected_recommendations.append(
                "Reduzir balanço ou profundidade de corte e revisar a rigidez antes da homologação."
            )
        if energy_risk:
            expected_recommendations.append(
                "Reduzir a carga de corte e conferir a capacidade nominal da máquina."
            )
        if wear_risk:
            expected_recommendations.append(
                "Planejar inspeção ou troca da aresta antes de qualquer aplicação física."
            )
        if not expected_recommendations:
            expected_recommendations.append(
                "Manter revisão humana e homologação de processo antes de qualquer aplicação física."
            )
        comparisons = (
            (
                self.dimensional_risk_score,
                expected_dimensional,
                "RISK_MATRIX_DIMENSIONAL_SCORE_INCONSISTENT",
            ),
            (
                self.dynamic_risk_score,
                expected_dynamic,
                "RISK_MATRIX_DYNAMIC_SCORE_INCONSISTENT",
            ),
            (
                self.energy_risk_score,
                expected_energy,
                "RISK_MATRIX_ENERGY_SCORE_INCONSISTENT",
            ),
            (
                self.tool_wear_risk_score,
                expected_wear,
                "RISK_MATRIX_TOOL_WEAR_SCORE_INCONSISTENT",
            ),
            (
                self.overall_risk_score,
                expected_overall,
                "RISK_MATRIX_OVERALL_SCORE_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        if self.risk_level != expected_level:
            raise ValueError("RISK_MATRIX_LEVEL_INCONSISTENT")
        if self.mitigation_recommendations != tuple(expected_recommendations):
            raise ValueError("RISK_MATRIX_RECOMMENDATIONS_INCONSISTENT")
        return self


class RawStockDimensions(_CNCGenerationContract):
    diameter_mm: float = Field(gt=0)
    axial_length_mm: float = Field(gt=0)
    z_min_mm: float
    z_max_mm: float

    @model_validator(mode="after")
    def validate_dimensions(self) -> "RawStockDimensions":
        if self.z_min_mm >= self.z_max_mm or not math.isclose(
            self.axial_length_mm,
            self.z_max_mm - self.z_min_mm,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("PROCESS_SHEET_RAW_STOCK_DIMENSIONS_INCONSISTENT")
        return self


class ProcessSheetClampingSetup(_CNCGenerationContract):
    setup_type: Literal["DECLARED_CHUCK_ENVELOPE_REQUIRES_MANUAL_SETUP"] = (
        "DECLARED_CHUCK_ENVELOPE_REQUIRES_MANUAL_SETUP"
    )
    chuck_exclusion_zone: ChuckExclusionZone2D
    minimum_clearance_mm: float = Field(gt=0)
    proximity_threshold_mm: float = Field(gt=0)
    estimated_setup_time_min: float = Field(gt=0)
    clamping_instruction: Literal[
        "CONFIRM_CHUCK_CONTACT_AND_STOCK_PROJECTION_MANUALLY_BEFORE_PROCESS_APPROVAL"
    ] = "CONFIRM_CHUCK_CONTACT_AND_STOCK_PROJECTION_MANUALLY_BEFORE_PROCESS_APPROVAL"
    balance_requirement: Literal[
        "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED"
    ] = "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED"


class OperationStep(_CNCGenerationContract):
    sequence: int = Field(ge=1, le=1_001)
    operation_id: str = Field(pattern=r"^OP\d{3,4}$")
    phase: Literal["SETUP", "FACING", "ROUGH_TURNING", "FINISHING", "GROOVING"]
    source_pass_sequence: int | None = Field(default=None, ge=1, le=1_000)
    tool_id: str | None = Field(default=None, min_length=1, max_length=64)
    tool_description: str | None = Field(default=None, min_length=1, max_length=128)
    insert_reference: str | None = Field(default=None, min_length=1, max_length=128)
    cutting_speed_vc_m_per_min: float | None = Field(default=None, gt=0)
    feed_mm_per_rev: float | None = Field(default=None, gt=0)
    depth_of_cut_ap_mm: float | None = Field(default=None, gt=0)
    spindle_rpm: float | None = Field(default=None, gt=0)
    feed_rate_mm_min: float | None = Field(default=None, gt=0)
    estimated_time_min: float = Field(ge=0)
    fixture_requirement: Literal[
        "USE_DECLARED_CHUCK_ENVELOPE_AND_VERIFY_CLEARANCE_MANUALLY"
    ] = "USE_DECLARED_CHUCK_ENVELOPE_AND_VERIFY_CLEARANCE_MANUALLY"
    balance_requirement: Literal[
        "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED"
    ] = "MANUAL_STATIC_AND_DYNAMIC_BALANCE_REVIEW_REQUIRED"

    @model_validator(mode="after")
    def validate_step(self) -> "OperationStep":
        machining_values = (
            self.tool_id,
            self.tool_description,
            self.insert_reference,
            self.cutting_speed_vc_m_per_min,
            self.feed_mm_per_rev,
            self.depth_of_cut_ap_mm,
            self.spindle_rpm,
            self.feed_rate_mm_min,
        )
        if self.phase == "SETUP":
            if self.source_pass_sequence is not None or any(
                value is not None for value in machining_values
            ):
                raise ValueError("PROCESS_SHEET_SETUP_PARAMETERS_INVALID")
            return self
        if self.source_pass_sequence is None or any(
            value is None for value in machining_values
        ):
            raise ValueError("PROCESS_SHEET_OPERATION_PARAMETERS_REQUIRED")
        assert self.feed_mm_per_rev is not None
        assert self.spindle_rpm is not None
        assert self.feed_rate_mm_min is not None
        if not math.isclose(
            self.feed_rate_mm_min,
            self.feed_mm_per_rev * self.spindle_rpm,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("PROCESS_SHEET_FEED_RATE_INCONSISTENT")
        return self


class MachiningProcessSheetPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-machining-process-sheet/v1"] = (
        "vena-ia.cnc-machining-process-sheet/v1"
    )
    part_id: str = Field(min_length=1, max_length=255)
    revision: str = Field(min_length=1, max_length=32)
    source_plan_id: str = Field(min_length=1, max_length=255)
    source_cam_plan: TurningStrategyPlanResponse
    source_stock: TurningStock2D
    source_machine_envelope: MachineEnvelope2D
    source_chuck_proximity: ChuckProximityAudit
    source_cycle_time_estimate: CycleTimeEstimatePayload
    raw_stock_dimensions: RawStockDimensions
    clamping_setup: ProcessSheetClampingSetup
    sequence_operations: tuple[OperationStep, ...] = Field(min_length=2, max_length=1_001)
    total_operations_count: int = Field(ge=2, le=1_001)
    estimated_total_time_min: float = Field(gt=0)
    safety_instructions: tuple[str, ...] = Field(min_length=3)
    is_theoretical_sheet: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_PROCESS_SHEET_REQUIRES_MACHINE_SETUP_APPROVAL"
    ] = "ANALYTICAL_PROCESS_SHEET_REQUIRES_MACHINE_SETUP_APPROVAL"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_process_sheet(self) -> "MachiningProcessSheetPayload":
        expected_raw = self.raw_stock_dimensions
        if (
            not math.isclose(expected_raw.diameter_mm, self.source_stock.diameter_mm, abs_tol=5e-9)
            or not math.isclose(expected_raw.z_min_mm, self.source_stock.z_min_mm, abs_tol=5e-9)
            or not math.isclose(expected_raw.z_max_mm, self.source_stock.z_max_mm, abs_tol=5e-9)
        ):
            raise ValueError("PROCESS_SHEET_STOCK_SOURCE_INCONSISTENT")
        clamping = self.clamping_setup
        if (
            clamping.chuck_exclusion_zone != self.source_machine_envelope.chuck_exclusion_zone
            or not math.isclose(
                clamping.minimum_clearance_mm,
                self.source_chuck_proximity.minimum_clearance_mm,
                abs_tol=5e-9,
            )
            or not math.isclose(
                clamping.proximity_threshold_mm,
                self.source_chuck_proximity.threshold_mm,
                abs_tol=5e-9,
            )
        ):
            raise ValueError("PROCESS_SHEET_CLAMPING_SOURCE_INCONSISTENT")
        if self.source_chuck_proximity.minimum_clearance_mm <= 0:
            raise ValueError("PROCESS_SHEET_CLAMPING_CLEARANCE_INVALID")
        operations = self.sequence_operations
        if self.total_operations_count != len(operations):
            raise ValueError("PROCESS_SHEET_OPERATION_COUNT_INCONSISTENT")
        if tuple(item.sequence for item in operations) != tuple(range(1, len(operations) + 1)):
            raise ValueError("PROCESS_SHEET_SEQUENCE_INVALID")
        if tuple(item.operation_id for item in operations) != tuple(
            f"OP{index * 10:03d}" for index in range(1, len(operations) + 1)
        ):
            raise ValueError("PROCESS_SHEET_OPERATION_ID_INCONSISTENT")
        if operations[0].phase != "SETUP" or any(
            item.phase == "SETUP" for item in operations[1:]
        ):
            raise ValueError("PROCESS_SHEET_SETUP_SEQUENCE_INVALID")
        passes = self.source_cam_plan.passes
        if tuple(item.sequence for item in passes) != tuple(range(1, len(passes) + 1)):
            raise ValueError("PROCESS_SHEET_CAM_SEQUENCE_INVALID")
        if any(item.operation_type != self.source_cam_plan.operation_type for item in passes):
            raise ValueError("PROCESS_SHEET_CAM_OPERATION_INCONSISTENT")
        machining_steps = operations[1:]
        if len(machining_steps) != len(passes) or any(
            step.source_pass_sequence != source.sequence
            or step.phase != source.operation_type.value
            for step, source in zip(machining_steps, passes)
        ):
            raise ValueError("PROCESS_SHEET_CAM_SOURCE_INCONSISTENT")
        setup_time = operations[0].estimated_time_min
        machining_time = math.fsum(item.estimated_time_min for item in machining_steps)
        source_cycle_minutes = self.source_cycle_time_estimate.total_cycle_time_seconds / 60.0
        if (
            not math.isclose(setup_time, clamping.estimated_setup_time_min, abs_tol=5e-9)
            or not math.isclose(machining_time, source_cycle_minutes, abs_tol=5e-9)
            or not math.isclose(
                self.estimated_total_time_min,
                setup_time + machining_time,
                abs_tol=5e-9,
            )
        ):
            raise ValueError("PROCESS_SHEET_TIME_SOURCE_INCONSISTENT")
        return self


class ResidualStockSection(_CNCGenerationContract):
    front_z_mm: float
    rear_z_mm: float
    nominal_radius_mm: float = Field(gt=0)
    in_process_radius_mm: float = Field(ge=0)
    residual_stock_mm: float

    @model_validator(mode="after")
    def validate_section(self) -> "ResidualStockSection":
        if self.front_z_mm <= self.rear_z_mm:
            raise ValueError("RESIDUAL_STOCK_SECTION_Z_INVALID")
        if not math.isclose(
            self.residual_stock_mm,
            self.in_process_radius_mm - self.nominal_radius_mm,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("RESIDUAL_STOCK_SECTION_DELTA_INCONSISTENT")
        return self


class MachiningResidualStockAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-residual-stock-audit/v1"] = (
        "vena-ia.cnc-residual-stock-audit/v1"
    )
    source_plan_id: str = Field(min_length=1, max_length=255)
    source_cam_plan: TurningStrategyPlanResponse
    source_nominal_profile: tuple[RzPoint, ...] = Field(min_length=2, max_length=10_000)
    stock_radius_mm: float = Field(gt=0)
    finish_allowance_nominal_mm: float = Field(ge=0, le=5.0)
    linear_tolerance_mm: float = Field(gt=0, le=1.0)
    tool_cutting_edge_length_mm: float = Field(gt=0)
    sections: tuple[ResidualStockSection, ...] = Field(min_length=1, max_length=10_000)
    max_residual_stock_mm: float
    min_residual_stock_mm: float
    average_stock_allowance_mm: float
    gouging_detected: bool
    status: Literal[
        "UNIFORM_ALLOWANCE_COMPLIANT",
        "EXCESS_MATERIAL_DETECTED",
        "CRITICAL_GOUGING_VIOLATION",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_RESIDUAL_STOCK_AUDIT_DOES_NOT_REPLACE_PHYSICAL_CMM_MEASUREMENT"
    ] = "ANALYTICAL_RESIDUAL_STOCK_AUDIT_DOES_NOT_REPLACE_PHYSICAL_CMM_MEASUREMENT"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_audit(self) -> "MachiningResidualStockAuditPayload":
        nominal_spans = [
            (
                max(first.z_mm, second.z_mm),
                min(first.z_mm, second.z_mm),
                first.r_mm,
            )
            for first, second in zip(
                self.source_nominal_profile,
                self.source_nominal_profile[1:],
            )
            if first.r_mm > self.linear_tolerance_mm
            and math.isclose(
                first.r_mm,
                second.r_mm,
                abs_tol=self.linear_tolerance_mm,
                rel_tol=0,
            )
            and abs(first.z_mm - second.z_mm) > self.linear_tolerance_mm
        ]
        nominal_spans.sort(key=lambda item: (-item[0], -item[1]))
        if len(nominal_spans) != len(self.sections):
            raise ValueError("RESIDUAL_STOCK_SECTION_SOURCE_INCONSISTENT")
        if any(
            not math.isclose(
                current[1],
                following[0],
                abs_tol=self.linear_tolerance_mm,
                rel_tol=0,
            )
            for current, following in zip(nominal_spans, nominal_spans[1:])
        ):
            raise ValueError("RESIDUAL_STOCK_PROFILE_SPANS_DISCONTINUOUS")
        if max(point.r_mm for point in self.source_nominal_profile) > (
            self.stock_radius_mm + self.linear_tolerance_mm
        ):
            raise ValueError("RESIDUAL_STOCK_PROFILE_OUTSIDE_STOCK")
        if any(
            abs(current[2] - following[2])
            > self.tool_cutting_edge_length_mm + self.linear_tolerance_mm
            for current, following in zip(nominal_spans, nominal_spans[1:])
        ):
            raise ValueError("RESIDUAL_STOCK_STEP_TOOL_INCOMPATIBLE")
        for section, (front_z, rear_z, nominal_radius) in zip(self.sections, nominal_spans):
            source_comparisons = (
                (section.front_z_mm, front_z),
                (section.rear_z_mm, rear_z),
                (section.nominal_radius_mm, nominal_radius),
            )
            if any(
                not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12)
                for actual, expected in source_comparisons
            ):
                raise ValueError("RESIDUAL_STOCK_SECTION_SOURCE_INCONSISTENT")
            midpoint_z = (front_z + rear_z) / 2.0
            reached_radii = [self.stock_radius_mm]
            for machining_pass in self.source_cam_plan.passes:
                for first, second in zip(
                    machining_pass.coordinates_rz_mm,
                    machining_pass.coordinates_rz_mm[1:],
                ):
                    delta_z = second.z_mm - first.z_mm
                    if abs(delta_z) <= self.linear_tolerance_mm:
                        continue
                    if midpoint_z < min(first.z_mm, second.z_mm) - self.linear_tolerance_mm:
                        continue
                    if midpoint_z > max(first.z_mm, second.z_mm) + self.linear_tolerance_mm:
                        continue
                    fraction = (midpoint_z - first.z_mm) / delta_z
                    reached_radii.append(first.r_mm + fraction * (second.r_mm - first.r_mm))
            if not math.isclose(
                section.in_process_radius_mm,
                min(reached_radii),
                abs_tol=5e-9,
                rel_tol=1e-12,
            ):
                raise ValueError("RESIDUAL_STOCK_CAM_SOURCE_INCONSISTENT")
        residuals = tuple(item.residual_stock_mm for item in self.sections)
        expected_min = min(residuals)
        expected_max = max(residuals)
        expected_average = math.fsum(residuals) / len(residuals)
        comparisons = (
            (self.min_residual_stock_mm, expected_min),
            (self.max_residual_stock_mm, expected_max),
            (self.average_stock_allowance_mm, expected_average),
        )
        if any(
            not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12)
            for actual, expected in comparisons
        ):
            raise ValueError("RESIDUAL_STOCK_AGGREGATE_INCONSISTENT")
        expected_gouging = expected_min < 0
        expected_status = (
            "CRITICAL_GOUGING_VIOLATION"
            if expected_gouging
            else "EXCESS_MATERIAL_DETECTED"
            if expected_max > self.finish_allowance_nominal_mm + 0.05
            else "UNIFORM_ALLOWANCE_COMPLIANT"
        )
        if self.gouging_detected != expected_gouging or self.status != expected_status:
            raise ValueError("RESIDUAL_STOCK_STATUS_INCONSISTENT")
        return self


class PartElasticDeflectionAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-part-elastic-deflection-audit/v1"] = (
        "vena-ia.cnc-part-elastic-deflection-audit/v1"
    )
    part_unsupported_length_mm: float = Field(gt=0)
    minimum_diameter_mm: float = Field(gt=0)
    radial_cutting_force_n: float = Field(gt=0)
    young_modulus_mpa: float = Field(gt=0)
    second_moment_area_mm4: float = Field(gt=0)
    calculated_stiffness_n_per_mm: float = Field(gt=0)
    radial_tolerance_mm: float = Field(gt=0)
    max_deflection_um: float = Field(gt=0)
    deflection_status: Literal[
        "ELASTIC_DEFLECTION_COMPLIANT",
        "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING",
    ]
    theoretical: Literal[True] = True
    physical: Literal[False] = False
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_PART_DEFLECTION_EXCLUDES_TAILSTOCK_AND_STEADY_REST_SUPPORT"
    ] = "ANALYTICAL_PART_DEFLECTION_EXCLUDES_TAILSTOCK_AND_STEADY_REST_SUPPORT"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_analytical_model(self) -> "PartElasticDeflectionAuditPayload":
        expected_area = math.pi * self.minimum_diameter_mm**4 / 64.0
        expected_stiffness = (
            3.0 * self.young_modulus_mpa * expected_area
            / self.part_unsupported_length_mm**3
        )
        expected_deflection_um = self.radial_cutting_force_n / expected_stiffness * 1_000.0
        comparisons = (
            (
                self.second_moment_area_mm4,
                expected_area,
                "PART_DEFLECTION_SECOND_MOMENT_INCONSISTENT",
            ),
            (
                self.calculated_stiffness_n_per_mm,
                expected_stiffness,
                "PART_DEFLECTION_STIFFNESS_INCONSISTENT",
            ),
            (
                self.max_deflection_um,
                expected_deflection_um,
                "PART_DEFLECTION_VALUE_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "PART_DEFLECTION_EXCEEDS_TOLERANCE_WARNING"
            if self.max_deflection_um > self.radial_tolerance_mm * 1_000.0
            else "ELASTIC_DEFLECTION_COMPLIANT"
        )
        if self.deflection_status != expected_status:
            raise ValueError("PART_DEFLECTION_STATUS_INCONSISTENT")
        return self


class SpindlePowerTorqueCurvePoint(_CNCGenerationContract):
    spindle_rpm: float = Field(gt=0, le=30_000)
    available_torque_nm: float = Field(gt=0)
    available_power_kw: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_power_torque_relation(self) -> "SpindlePowerTorqueCurvePoint":
        expected_power = (
            self.available_torque_nm * 2.0 * math.pi * self.spindle_rpm / 60_000.0
        )
        if not math.isclose(
            self.available_power_kw,
            expected_power,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("SPINDLE_CURVE_POWER_TORQUE_INCONSISTENT")
        return self


class SpindlePowerTorqueOperatingPoint(_CNCGenerationContract):
    spindle_rpm: float = Field(gt=0, le=30_000)
    required_cutting_power_kw: float = Field(gt=0)
    required_torque_nm: float = Field(gt=0)
    available_power_kw: float = Field(gt=0)
    available_torque_nm: float = Field(gt=0)
    power_margin_kw: float
    power_margin_percent: float
    torque_margin_nm: float
    status: Literal[
        "WITHIN_POWER_TORQUE_ENVELOPE",
        "POWER_TORQUE_ENVELOPE_EXCEEDED",
    ]

    @model_validator(mode="after")
    def validate_operating_point(self) -> "SpindlePowerTorqueOperatingPoint":
        angular_factor = 2.0 * math.pi * self.spindle_rpm / 60_000.0
        expected_required_torque = self.required_cutting_power_kw / angular_factor
        expected_available_power = self.available_torque_nm * angular_factor
        comparisons = (
            (
                self.required_torque_nm,
                expected_required_torque,
                "SPINDLE_REQUIRED_TORQUE_INCONSISTENT",
            ),
            (
                self.available_power_kw,
                expected_available_power,
                "SPINDLE_AVAILABLE_POWER_INCONSISTENT",
            ),
            (
                self.power_margin_kw,
                self.available_power_kw - self.required_cutting_power_kw,
                "SPINDLE_POWER_MARGIN_INCONSISTENT",
            ),
            (
                self.power_margin_percent,
                ((self.available_power_kw - self.required_cutting_power_kw) / self.available_power_kw)
                * 100.0,
                "SPINDLE_POWER_MARGIN_PERCENT_INCONSISTENT",
            ),
            (
                self.torque_margin_nm,
                self.available_torque_nm - self.required_torque_nm,
                "SPINDLE_TORQUE_MARGIN_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "WITHIN_POWER_TORQUE_ENVELOPE"
            if self.power_margin_kw >= 0 and self.torque_margin_nm >= 0
            else "POWER_TORQUE_ENVELOPE_EXCEEDED"
        )
        if self.status != expected_status:
            raise ValueError("SPINDLE_OPERATING_POINT_STATUS_INCONSISTENT")
        return self


class SpindlePowerTorqueEnvelopeAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-spindle-power-torque-envelope-audit/v2"] = (
        "vena-ia.cnc-spindle-power-torque-envelope-audit/v2"
    )
    source_power_force_audit: MachiningPowerForceAuditPayload
    spindle_rpm_min: float = Field(gt=0, le=30_000)
    spindle_rpm_max: float = Field(gt=0, le=30_000)
    curve_points: tuple[SpindlePowerTorqueCurvePoint, ...] = Field(
        min_length=2,
        max_length=1_000,
    )
    operating_points: tuple[SpindlePowerTorqueOperatingPoint, ...] = Field(
        min_length=1,
        max_length=1_000,
    )
    audit_status: Literal[
        "POWER_TORQUE_ENVELOPE_COMPLIANT",
        "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "DECLARED_SPINDLE_POWER_TORQUE_CURVE_REQUIRES_MACHINE_PROFILE_VALIDATION"
    ] = "DECLARED_SPINDLE_POWER_TORQUE_CURVE_REQUIRES_MACHINE_PROFILE_VALIDATION"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_envelope_sources(self) -> "SpindlePowerTorqueEnvelopeAuditPayload":
        curve_rpms = tuple(point.spindle_rpm for point in self.curve_points)
        if any(current >= following for current, following in zip(curve_rpms, curve_rpms[1:])):
            raise ValueError("SPINDLE_CURVE_RPM_ORDER_INVALID")
        if (
            not math.isclose(self.spindle_rpm_min, curve_rpms[0], abs_tol=5e-9)
            or not math.isclose(self.spindle_rpm_max, curve_rpms[-1], abs_tol=5e-9)
            or self.spindle_rpm_max > self.source_power_force_audit.max_spindle_rpm
        ):
            raise ValueError("SPINDLE_CURVE_RANGE_INCONSISTENT")

        operating_rpms = tuple(point.spindle_rpm for point in self.operating_points)
        if any(current >= following for current, following in zip(operating_rpms, operating_rpms[1:])):
            raise ValueError("SPINDLE_OPERATING_POINT_RPM_ORDER_INVALID")
        if not any(
            math.isclose(
                rpm,
                self.source_power_force_audit.spindle_rpm_reference,
                abs_tol=5e-9,
            )
            for rpm in operating_rpms
        ):
            raise ValueError("SPINDLE_REFERENCE_RPM_NOT_AUDITED")

        for operating in self.operating_points:
            if operating.spindle_rpm < self.spindle_rpm_min or operating.spindle_rpm > (
                self.spindle_rpm_max
            ):
                raise ValueError("SPINDLE_OPERATING_POINT_OUTSIDE_CURVE")
            if not math.isclose(
                operating.required_cutting_power_kw,
                self.source_power_force_audit.pc_cutting_kw,
                abs_tol=5e-9,
                rel_tol=1e-12,
            ):
                raise ValueError("SPINDLE_POWER_FORCE_SOURCE_INCONSISTENT")
            lower, upper = next(
                (first, second)
                for first, second in zip(self.curve_points, self.curve_points[1:])
                if first.spindle_rpm <= operating.spindle_rpm <= second.spindle_rpm
            )
            fraction = (
                (operating.spindle_rpm - lower.spindle_rpm)
                / (upper.spindle_rpm - lower.spindle_rpm)
            )
            expected_torque = lower.available_torque_nm + fraction * (
                upper.available_torque_nm - lower.available_torque_nm
            )
            if not math.isclose(
                operating.available_torque_nm,
                expected_torque,
                abs_tol=5e-9,
                rel_tol=1e-12,
            ):
                raise ValueError("SPINDLE_CURVE_INTERPOLATION_INCONSISTENT")

        expected_status = (
            "POWER_TORQUE_ENVELOPE_EXCEEDED_WARNING"
            if any(
                point.status == "POWER_TORQUE_ENVELOPE_EXCEEDED"
                for point in self.operating_points
            )
            else "POWER_TORQUE_ENVELOPE_COMPLIANT"
        )
        if self.audit_status != expected_status:
            raise ValueError("SPINDLE_POWER_TORQUE_AUDIT_STATUS_INCONSISTENT")
        return self


class ThermalExpansionDriftAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-thermal-expansion-drift-audit/v2"] = (
        "vena-ia.cnc-thermal-expansion-drift-audit/v2"
    )
    material_profile: Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
    linear_expansion_coefficient_per_c: float = Field(gt=0, le=0.001)
    spindle_expansion_coefficient_per_c: float = Field(gt=0, le=0.001)
    reference_temperature_c: float = Field(default=20.0, ge=20.0, le=20.0)
    workpiece_mean_temperature_c: float = Field(ge=-40, le=300)
    spindle_mean_temperature_c: float = Field(ge=-40, le=300)
    workpiece_mean_temperature_rise_c: float = Field(ge=0, le=500)
    spindle_mean_temperature_rise_c: float = Field(ge=0, le=500)
    workpiece_axial_reference_length_mm: float = Field(gt=0, le=100_000)
    workpiece_diameter_reference_mm: float = Field(gt=0, le=100_000)
    spindle_z_reference_length_mm: float = Field(gt=0, le=100_000)
    workpiece_z_expansion_um: float = Field(ge=0)
    workpiece_x_expansion_um: float = Field(ge=0)
    spindle_z_drift_um: float = Field(ge=0)
    total_z_axis_drift_um: float = Field(ge=0)
    total_x_axis_drift_um: float = Field(ge=0)
    z_axis_tolerance_um: float = Field(gt=0)
    x_axis_tolerance_um: float = Field(gt=0)
    audit_status: Literal[
        "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE",
        "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING",
    ]
    theoretical: Literal[True] = True
    physical: Literal[False] = False
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_THERMAL_DRIFT_EXCLUDES_TRANSIENT_GRADIENTS_COOLANT_AND_MACHINE_COMPENSATION"
    ] = "ANALYTICAL_THERMAL_DRIFT_EXCLUDES_TRANSIENT_GRADIENTS_COOLANT_AND_MACHINE_COMPENSATION"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_thermal_expansion_model(self) -> "ThermalExpansionDriftAuditPayload":
        expected_coefficient = {
            "AISI_1020": 12.0e-6,
            "ABNT_1045": 12.0e-6,
            "ALUMINUM_6061_T6": 23.0e-6,
        }[self.material_profile]
        if not math.isclose(
            self.linear_expansion_coefficient_per_c,
            expected_coefficient,
            abs_tol=5e-12,
            rel_tol=1e-12,
        ):
            raise ValueError("THERMAL_EXPANSION_COEFFICIENT_INCONSISTENT")
        if not math.isclose(
            self.spindle_expansion_coefficient_per_c,
            12.0e-6,
            abs_tol=5e-12,
            rel_tol=1e-12,
        ):
            raise ValueError("THERMAL_SPINDLE_COEFFICIENT_INCONSISTENT")
        if not math.isclose(
            self.workpiece_mean_temperature_rise_c,
            self.workpiece_mean_temperature_c - self.reference_temperature_c,
            abs_tol=5e-9,
        ) or not math.isclose(
            self.spindle_mean_temperature_rise_c,
            self.spindle_mean_temperature_c - self.reference_temperature_c,
            abs_tol=5e-9,
        ):
            raise ValueError("THERMAL_DELTA_TEMPERATURE_INCONSISTENT")

        alpha = self.linear_expansion_coefficient_per_c
        workpiece_temperature = self.workpiece_mean_temperature_rise_c
        spindle_temperature = self.spindle_mean_temperature_rise_c
        expected = (
            (
                self.workpiece_z_expansion_um,
                alpha * self.workpiece_axial_reference_length_mm * workpiece_temperature * 1_000,
                "THERMAL_WORKPIECE_Z_EXPANSION_INCONSISTENT",
            ),
            (
                self.workpiece_x_expansion_um,
                alpha * (self.workpiece_diameter_reference_mm / 2.0) * workpiece_temperature * 1_000,
                "THERMAL_WORKPIECE_X_EXPANSION_INCONSISTENT",
            ),
            (
                self.spindle_z_drift_um,
                self.spindle_expansion_coefficient_per_c
                * self.spindle_z_reference_length_mm
                * spindle_temperature
                * 1_000,
                "THERMAL_SPINDLE_Z_DRIFT_INCONSISTENT",
            ),
        )
        for actual, calculated, code in expected:
            if not math.isclose(actual, calculated, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        if not math.isclose(
            self.total_z_axis_drift_um,
            self.workpiece_z_expansion_um + self.spindle_z_drift_um,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("THERMAL_TOTAL_Z_DRIFT_INCONSISTENT")
        if not math.isclose(
            self.total_x_axis_drift_um,
            self.workpiece_x_expansion_um,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("THERMAL_TOTAL_X_DRIFT_INCONSISTENT")
        expected_status = (
            "THERMAL_DRIFT_EXCEEDS_DECLARED_TOLERANCE_WARNING"
            if self.total_z_axis_drift_um > self.z_axis_tolerance_um
            or self.total_x_axis_drift_um > self.x_axis_tolerance_um
            else "THERMAL_DRIFT_WITHIN_DECLARED_TOLERANCE"
        )
        if self.audit_status != expected_status:
            raise ValueError("THERMAL_DRIFT_STATUS_INCONSISTENT")
        return self


class ToolWearGeometryAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-tool-wear-geometry-audit/v2"] = (
        "vena-ia.cnc-tool-wear-geometry-audit/v2"
    )
    source_tool_life_audit: ToolLifeTaylorAuditPayload
    nominal_nose_radius_mm: float = Field(gt=0, le=100)
    clearance_angle_deg: float = Field(gt=0, lt=90)
    position_angle_deg: float = Field(gt=0, lt=180)
    maximum_allowable_flank_wear_vb_mm: float = Field(gt=0, le=5)
    estimated_flank_wear_vb_mm: float = Field(ge=0, le=5)
    flank_wear_progress_percent: float = Field(ge=0)
    effective_nose_radius_mm: float = Field(gt=0, le=100)
    predicted_radial_deviation_um: float = Field(ge=0)
    predicted_axial_deviation_um: float = Field(ge=0)
    geometry_tolerance_um: float = Field(gt=0)
    audit_status: Literal[
        "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE",
        "TOOL_WEAR_EXCEEDS_TOLERANCE_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    compensation_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_TOOL_WEAR_GEOMETRY_DOES_NOT_AUTHORIZE_AUTOMATIC_OFFSET_COMPENSATION"
    ] = "ANALYTICAL_TOOL_WEAR_GEOMETRY_DOES_NOT_AUTHORIZE_AUTOMATIC_OFFSET_COMPENSATION"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_progressive_wear_model(self) -> "ToolWearGeometryAuditPayload":
        expected_progress = self.source_tool_life_audit.tool_life_consumed_percent
        if math.isclose(self.position_angle_deg, 90.0, abs_tol=1e-9):
            raise ValueError("TOOL_WEAR_POSITION_ANGLE_INVALID")
        expected_wear = self.maximum_allowable_flank_wear_vb_mm * math.sqrt(
            expected_progress / 100.0
        )
        radial_deviation = expected_wear * math.tan(math.radians(self.clearance_angle_deg))
        effective_position_angle = min(self.position_angle_deg, 180.0 - self.position_angle_deg)
        axial_deviation = radial_deviation / math.tan(math.radians(effective_position_angle))
        expected_radius = self.nominal_nose_radius_mm + radial_deviation / 2.0
        if expected_radius <= 0:
            raise ValueError("TOOL_WEAR_EFFECTIVE_NOSE_RADIUS_NON_PHYSICAL")
        comparisons = (
            (self.flank_wear_progress_percent, expected_progress, "TOOL_WEAR_PROGRESS_INCONSISTENT"),
            (self.estimated_flank_wear_vb_mm, expected_wear, "TOOL_WEAR_VB_MAX_INCONSISTENT"),
            (self.effective_nose_radius_mm, expected_radius, "TOOL_WEAR_NOSE_RADIUS_INCONSISTENT"),
            (self.predicted_radial_deviation_um, radial_deviation * 1_000.0, "TOOL_WEAR_RADIAL_DEVIATION_INCONSISTENT"),
            (self.predicted_axial_deviation_um, axial_deviation * 1_000.0, "TOOL_WEAR_AXIAL_DEVIATION_INCONSISTENT"),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "TOOL_WEAR_EXCEEDS_TOLERANCE_WARNING"
            if self.predicted_radial_deviation_um > self.geometry_tolerance_um * 0.5
            else "TOOL_WEAR_GEOMETRY_WITHIN_TOLERANCE"
        )
        if self.audit_status != expected_status:
            raise ValueError("TOOL_WEAR_GEOMETRY_STATUS_INCONSISTENT")
        return self


class ChipBreakerSafeEnvelope(_CNCGenerationContract):
    chipbreaker_reference: str = Field(min_length=1, max_length=120)
    feed_min_mm_per_rev: float = Field(gt=0, le=10)
    feed_max_mm_per_rev: float = Field(gt=0, le=10)
    depth_of_cut_min_mm: float = Field(gt=0, le=100)
    depth_of_cut_max_mm: float = Field(gt=0, le=100)

    @model_validator(mode="after")
    def validate_ordered_limits(self) -> "ChipBreakerSafeEnvelope":
        if (
            self.feed_max_mm_per_rev <= self.feed_min_mm_per_rev
            or self.depth_of_cut_max_mm <= self.depth_of_cut_min_mm
        ):
            raise ValueError("CHIP_BREAKER_SAFE_ENVELOPE_INVALID")
        return self


class ChipBreakingMachinabilityAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-chip-breaking-machinability-audit/v2"] = (
        "vena-ia.cnc-chip-breaking-machinability-audit/v2"
    )
    material_profile: Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
    chipbreaker_family: Literal["PM", "PR", "PF"]
    chipbreaker_reference: str = Field(min_length=1, max_length=120)
    feed_mm_per_rev: float = Field(gt=0, le=10)
    depth_of_cut_mm: float = Field(gt=0, le=100)
    insert_nose_radius_mm: float = Field(gt=0, le=20)
    cutting_edge_angle_deg: float = Field(gt=0, lt=180)
    rake_angle_deg: float = Field(ge=-20, le=40)
    uncut_chip_thickness_mm: float = Field(gt=0, le=10)
    chip_width_mm: float = Field(gt=0, le=1_000)
    formed_chip_thickness_mm: float = Field(gt=0, le=100)
    chip_compression_ratio: float = Field(ge=1, le=100)
    free_chip_length_mm: float = Field(gt=0, le=10_000)
    safe_breaking_envelopes: tuple[ChipBreakerSafeEnvelope, ...] = Field(
        min_length=1
    )
    audit_status: Literal[
        "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE",
        "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    automatic_parameter_change_authorized: Literal[False] = False
    model_limitation: Literal[
        "TABULATED_CHIP_BREAKING_ENVELOPE_REQUIRES_PHYSICAL_PROCESS_VALIDATION"
    ] = "TABULATED_CHIP_BREAKING_ENVELOPE_REQUIRES_PHYSICAL_PROCESS_VALIDATION"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_chip_breaking_snapshot(self) -> "ChipBreakingMachinabilityAuditPayload":
        sin_kr = math.sin(math.radians(self.cutting_edge_angle_deg))
        if not math.isfinite(sin_kr) or sin_kr <= 0:
            raise ValueError("CHIP_BREAKING_CUTTING_EDGE_ANGLE_INVALID")
        expected_uncut_thickness = self.feed_mm_per_rev * sin_kr
        expected_width = self.depth_of_cut_mm / sin_kr
        base_compression_ratio = {
            "AISI_1020": 2.2,
            "ABNT_1045": 2.4,
            "ALUMINUM_6061_T6": 1.8,
        }[self.material_profile]
        expected_ratio = max(
            1.0,
            base_compression_ratio - 0.02 * (self.rake_angle_deg - 6.0),
        )
        expected_formed_thickness = expected_uncut_thickness * expected_ratio
        expected_free_chip_length = 2.0 * math.pi * (
            self.insert_nose_radius_mm + expected_formed_thickness
        )
        comparisons = (
            (
                self.uncut_chip_thickness_mm,
                expected_uncut_thickness,
                "CHIP_BREAKING_UNCUT_THICKNESS_INCONSISTENT",
            ),
            (self.chip_width_mm, expected_width, "CHIP_BREAKING_WIDTH_INCONSISTENT"),
            (
                self.chip_compression_ratio,
                expected_ratio,
                "CHIP_COMPRESSION_RATIO_INCONSISTENT",
            ),
            (
                self.formed_chip_thickness_mm,
                expected_formed_thickness,
                "CHIP_BREAKING_FORMED_THICKNESS_INCONSISTENT",
            ),
            (
                self.free_chip_length_mm,
                expected_free_chip_length,
                "CHIP_BREAKING_FREE_LENGTH_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        references = [item.chipbreaker_reference for item in self.safe_breaking_envelopes]
        if len(references) != len(set(references)):
            raise ValueError("CHIP_BREAKER_SAFE_ENVELOPE_DUPLICATE")
        expected_envelopes = {
            "CNMG_120408_PM_TABULATED": (0.15, 0.40, 1.0, 4.0),
            "CNMG_120408_PR_TABULATED": (0.25, 0.60, 2.0, 6.0),
            "CNMG_120408_PF_TABULATED": (0.05, 0.20, 0.2, 2.0),
        }
        if set(references) != set(expected_envelopes):
            raise ValueError("CHIP_BREAKER_SAFE_ENVELOPE_TABLE_INCONSISTENT")
        for item in self.safe_breaking_envelopes:
            actual_limits = (
                item.feed_min_mm_per_rev,
                item.feed_max_mm_per_rev,
                item.depth_of_cut_min_mm,
                item.depth_of_cut_max_mm,
            )
            if actual_limits != expected_envelopes[item.chipbreaker_reference]:
                raise ValueError("CHIP_BREAKER_SAFE_ENVELOPE_TABLE_INCONSISTENT")
        selected = [
            item
            for item in self.safe_breaking_envelopes
            if item.chipbreaker_reference == self.chipbreaker_reference
        ]
        if len(selected) != 1:
            raise ValueError("CHIP_BREAKER_SAFE_ENVELOPE_REFERENCE_UNRESOLVED")
        envelope = selected[0]
        expected_family = envelope.chipbreaker_reference.rsplit("_", 2)[-2]
        if self.chipbreaker_family != expected_family:
            raise ValueError("CHIP_BREAKER_FAMILY_INCONSISTENT")
        inside_envelope = (
            envelope.feed_min_mm_per_rev
            <= self.feed_mm_per_rev
            <= envelope.feed_max_mm_per_rev
            and envelope.depth_of_cut_min_mm
            <= self.depth_of_cut_mm
            <= envelope.depth_of_cut_max_mm
        )
        expected_status = (
            "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"
            if inside_envelope
            else "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING"
        )
        if self.audit_status != expected_status:
            raise ValueError("CHIP_BREAKING_AUDIT_STATUS_INCONSISTENT")
        return self


class CoolantZoneRequirement(_CNCGenerationContract):
    cutting_zone: Literal[
        "PRIMARY_SHEAR_ZONE",
        "SECONDARY_TOOL_CHIP_INTERFACE",
        "TERTIARY_TOOL_WORKPIECE_INTERFACE",
    ]
    minimum_flow_l_per_min: float = Field(gt=0, le=1_000)
    minimum_pressure_bar: float = Field(gt=0, le=1_000)


class CoolantPressureFlowAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-coolant-pressure-flow-audit/v2"] = (
        "vena-ia.cnc-coolant-pressure-flow-audit/v2"
    )
    coolant_mode: Literal["FLOOD", "MQL"]
    programmed_flow_l_per_min: float = Field(gt=0, le=1_000)
    programmed_pressure_bar: float = Field(gt=0, le=1_000)
    zone_requirements: tuple[CoolantZoneRequirement, ...] = Field(min_length=3, max_length=3)
    minimum_required_flow_l_per_min: float = Field(gt=0, le=1_000)
    minimum_required_pressure_bar: float = Field(gt=0, le=1_000)
    flow_margin_percent: float = Field(ge=-100, le=100_000)
    pressure_margin_percent: float = Field(ge=-100, le=100_000)
    thermal_dissipation_status: Literal[
        "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS",
        "INSUFFICIENT_THERMAL_DISSIPATION_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    automatic_coolant_control_authorized: Literal[False] = False
    model_limitation: Literal[
        "TABULATED_COOLANT_DEMAND_REQUIRES_MACHINE_AND_NOZZLE_PHYSICAL_VALIDATION"
    ] = "TABULATED_COOLANT_DEMAND_REQUIRES_MACHINE_AND_NOZZLE_PHYSICAL_VALIDATION"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_coolant_demand_snapshot(self) -> "CoolantPressureFlowAuditPayload":
        expected_tables = {
            "FLOOD": {
                "PRIMARY_SHEAR_ZONE": (12.0, 4.0),
                "SECONDARY_TOOL_CHIP_INTERFACE": (15.0, 6.0),
                "TERTIARY_TOOL_WORKPIECE_INTERFACE": (10.0, 3.0),
            },
            "MQL": {
                "PRIMARY_SHEAR_ZONE": (0.05, 5.0),
                "SECONDARY_TOOL_CHIP_INTERFACE": (0.08, 6.0),
                "TERTIARY_TOOL_WORKPIECE_INTERFACE": (0.04, 4.0),
            },
        }
        expected_table = expected_tables[self.coolant_mode]
        actual_table = {
            item.cutting_zone: (
                item.minimum_flow_l_per_min,
                item.minimum_pressure_bar,
            )
            for item in self.zone_requirements
        }
        if len(actual_table) != len(self.zone_requirements) or actual_table != expected_table:
            raise ValueError("COOLANT_ZONE_REQUIREMENTS_INCONSISTENT")
        required_flow = max(item.minimum_flow_l_per_min for item in self.zone_requirements)
        required_pressure = max(item.minimum_pressure_bar for item in self.zone_requirements)
        expected_flow_margin = (
            self.programmed_flow_l_per_min - required_flow
        ) / required_flow * 100.0
        expected_pressure_margin = (
            self.programmed_pressure_bar - required_pressure
        ) / required_pressure * 100.0
        comparisons = (
            (
                self.minimum_required_flow_l_per_min,
                required_flow,
                "COOLANT_MINIMUM_FLOW_INCONSISTENT",
            ),
            (
                self.minimum_required_pressure_bar,
                required_pressure,
                "COOLANT_MINIMUM_PRESSURE_INCONSISTENT",
            ),
            (self.flow_margin_percent, expected_flow_margin, "COOLANT_FLOW_MARGIN_INCONSISTENT"),
            (
                self.pressure_margin_percent,
                expected_pressure_margin,
                "COOLANT_PRESSURE_MARGIN_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "COOLANT_DEMAND_WITHIN_TABULATED_REQUIREMENTS"
            if self.programmed_flow_l_per_min >= required_flow
            and self.programmed_pressure_bar >= required_pressure
            else "INSUFFICIENT_THERMAL_DISSIPATION_WARNING"
        )
        if self.thermal_dissipation_status != expected_status:
            raise ValueError("COOLANT_THERMAL_DISSIPATION_STATUS_INCONSISTENT")
        return self


class WorkholdingClampingAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-workholding-clamping-audit/v1"] = (
        "vena-ia.cnc-workholding-clamping-audit/v1"
    )
    static_clamping_force_per_jaw_n: float = Field(gt=0, le=2_000_000)
    jaw_mass_kg: float = Field(ge=0.01, le=50)
    center_of_mass_radius_mm: float = Field(ge=1, le=1_000)
    operating_rpm: float = Field(gt=0, le=50_000)
    maximum_declared_rpm: float = Field(gt=0, le=50_000)
    axial_cutting_force_n: float = Field(gt=0, le=10_000_000)
    friction_coefficient: float = Field(gt=0, le=1)
    required_safety_factor: float = Field(ge=2, le=100)
    centrifugal_force_per_jaw_n: float = Field(gt=0)
    total_centrifugal_loss_n: float = Field(gt=0)
    dynamic_clamping_force_total_n: float = Field(gt=0)
    friction_resistance_n: float = Field(gt=0)
    clamping_safety_factor: float = Field(gt=0)
    clamping_status: Literal[
        "DYNAMIC_CLAMPING_SAFE",
        "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    automatic_chuck_control_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_CLAMPING_ESTIMATE_REQUIRES_PHYSICAL_CHUCK_LOAD_MEASUREMENT"
    ] = "ANALYTICAL_CLAMPING_ESTIMATE_REQUIRES_PHYSICAL_CHUCK_LOAD_MEASUREMENT"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_workholding_snapshot(self) -> "WorkholdingClampingAuditPayload":
        if self.operating_rpm > self.maximum_declared_rpm:
            raise ValueError("WORKHOLDING_OPERATING_RPM_EXCEEDS_DECLARED_LIMIT")
        angular_velocity = 2.0 * math.pi * self.operating_rpm / 60.0
        centrifugal_per_jaw = (
            self.jaw_mass_kg
            * (self.center_of_mass_radius_mm / 1_000.0)
            * angular_velocity**2
        )
        total_loss = 3.0 * centrifugal_per_jaw
        dynamic_force = 3.0 * self.static_clamping_force_per_jaw_n - total_loss
        if dynamic_force <= 0:
            raise ValueError("WORKHOLDING_TOTAL_CLAMPING_LOSS")
        friction_resistance = self.friction_coefficient * dynamic_force
        safety_factor = friction_resistance / self.axial_cutting_force_n
        comparisons = (
            (
                self.centrifugal_force_per_jaw_n,
                centrifugal_per_jaw,
                "WORKHOLDING_CENTRIFUGAL_FORCE_INCONSISTENT",
            ),
            (
                self.total_centrifugal_loss_n,
                total_loss,
                "WORKHOLDING_CENTRIFUGAL_LOSS_INCONSISTENT",
            ),
            (
                self.dynamic_clamping_force_total_n,
                dynamic_force,
                "WORKHOLDING_DYNAMIC_CLAMPING_FORCE_INCONSISTENT",
            ),
            (
                self.friction_resistance_n,
                friction_resistance,
                "WORKHOLDING_FRICTION_RESISTANCE_INCONSISTENT",
            ),
            (
                self.clamping_safety_factor,
                safety_factor,
                "WORKHOLDING_SAFETY_FACTOR_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "DYNAMIC_CLAMPING_SAFE"
            if safety_factor >= self.required_safety_factor
            else "CRITICAL_CENTRIFUGAL_CLAMPING_LOSS_WARNING"
        )
        if self.clamping_status != expected_status:
            raise ValueError("WORKHOLDING_CLAMPING_STATUS_INCONSISTENT")
        return self


class TailstockThrustAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-tailstock-thrust-audit/v1"] = (
        "vena-ia.cnc-tailstock-thrust-audit/v1"
    )
    tailstock_force_n: float = Field(gt=0, le=10_000_000)
    critical_buckling_load_n: float = Field(gt=0)
    max_supported_deflection_um: float = Field(gt=0)
    engagement_z_coordinate_mm: float
    total_supported_length_mm: float = Field(gt=0, le=100_000)
    minimum_diameter_mm: float = Field(gt=0, le=10_000)
    cutting_load_position_mm: float = Field(gt=0, le=100_000)
    radial_cutting_force_n: float = Field(gt=0, le=10_000_000)
    young_modulus_mpa: float = Field(gt=0, le=1_000_000)
    second_moment_area_mm4: float = Field(gt=0)
    effective_length_factor: float = Field(gt=0, le=2)
    warning_threshold_n: float = Field(gt=0)
    tailstock_status: Literal[
        "TAILSTOCK_SUPPORT_COMPLIANT",
        "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    automatic_tailstock_control_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_TAILSTOCK_SUPPORT_EXCLUDES_CENTER_ECCENTRICITY_AND_QUILL_BEARING_WEAR"
    ] = "ANALYTICAL_TAILSTOCK_SUPPORT_EXCLUDES_CENTER_ECCENTRICITY_AND_QUILL_BEARING_WEAR"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_tailstock_snapshot(self) -> "TailstockThrustAuditPayload":
        if self.cutting_load_position_mm >= self.total_supported_length_mm:
            raise ValueError("TAILSTOCK_CUTTING_POSITION_OUTSIDE_SUPPORT_SPAN")
        expected_second_moment = math.pi * self.minimum_diameter_mm**4 / 64.0
        distance_to_tailstock = (
            self.total_supported_length_mm - self.cutting_load_position_mm
        )
        expected_deflection_um = (
            self.radial_cutting_force_n
            * self.cutting_load_position_mm**2
            * distance_to_tailstock**2
            / (
                3.0
                * self.young_modulus_mpa
                * expected_second_moment
                * self.total_supported_length_mm
            )
            * 1_000.0
        )
        expected_critical_load = (
            math.pi**2
            * self.young_modulus_mpa
            * expected_second_moment
            / (self.effective_length_factor * self.total_supported_length_mm) ** 2
        )
        expected_threshold = 0.3 * expected_critical_load
        comparisons = (
            (
                self.second_moment_area_mm4,
                expected_second_moment,
                "TAILSTOCK_SECOND_MOMENT_INCONSISTENT",
            ),
            (
                self.max_supported_deflection_um,
                expected_deflection_um,
                "TAILSTOCK_DEFLECTION_INCONSISTENT",
            ),
            (
                self.critical_buckling_load_n,
                expected_critical_load,
                "TAILSTOCK_CRITICAL_BUCKLING_LOAD_INCONSISTENT",
            ),
            (
                self.warning_threshold_n,
                expected_threshold,
                "TAILSTOCK_WARNING_THRESHOLD_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "TAILSTOCK_THRUST_BUCKLING_RISK_WARNING"
            if self.tailstock_force_n > expected_threshold
            else "TAILSTOCK_SUPPORT_COMPLIANT"
        )
        if self.tailstock_status != expected_status:
            raise ValueError("TAILSTOCK_STATUS_INCONSISTENT")
        return self


class SpindleHarmonicDynamicsAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-spindle-harmonic-dynamics-audit/v1"] = (
        "vena-ia.cnc-spindle-harmonic-dynamics-audit/v1"
    )
    system_stiffness_n_per_m: float = Field(gt=0, le=1e21)
    effective_mass_kg: float = Field(gt=0, le=1e6)
    workpiece_mass_kg: float = Field(gt=0, le=1e6)
    mass_eccentricity_mm: float = Field(ge=0, le=100)
    natural_angular_frequency_rad_s: float = Field(gt=0)
    first_critical_rpm: float = Field(gt=0)
    operating_rpm: float = Field(gt=0, le=100_000)
    resonance_proximity_percent: float = Field(ge=0)
    resonance_exclusion_percent: float = Field(gt=0, lt=100)
    unbalance_force_n: float = Field(ge=0)
    bearing_admissible_force_n: float = Field(gt=0, le=100_000_000)
    dynamic_status: Literal[
        "SPINDLE_DYNAMICS_COMPLIANT",
        "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING",
        "DYNAMIC_UNBALANCE_EXCESSIVE_FORCE_WARNING",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    automatic_spindle_control_authorized: Literal[False] = False
    model_limitation: Literal[
        "ANALYTICAL_CRITICAL_SPEED_EXCLUDES_VISCOUS_DAMPING_AND_BEARING_RACE_DEFECTS"
    ] = "ANALYTICAL_CRITICAL_SPEED_EXCLUDES_VISCOUS_DAMPING_AND_BEARING_RACE_DEFECTS"
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_harmonic_snapshot(self) -> "SpindleHarmonicDynamicsAuditPayload":
        if self.effective_mass_kg > self.workpiece_mass_kg:
            raise ValueError("SPINDLE_HARMONIC_EFFECTIVE_MASS_INVALID")
        expected_natural_frequency = math.sqrt(
            self.system_stiffness_n_per_m / self.effective_mass_kg
        )
        expected_critical_rpm = expected_natural_frequency * 60.0 / (2.0 * math.pi)
        expected_proximity = (
            abs(self.operating_rpm - expected_critical_rpm) / expected_critical_rpm * 100.0
        )
        operating_angular_velocity = 2.0 * math.pi * self.operating_rpm / 60.0
        expected_unbalance_force = (
            self.workpiece_mass_kg
            * (self.mass_eccentricity_mm / 1_000.0)
            * operating_angular_velocity**2
        )
        comparisons = (
            (
                self.natural_angular_frequency_rad_s,
                expected_natural_frequency,
                "SPINDLE_HARMONIC_NATURAL_FREQUENCY_INCONSISTENT",
            ),
            (
                self.first_critical_rpm,
                expected_critical_rpm,
                "SPINDLE_HARMONIC_CRITICAL_RPM_INCONSISTENT",
            ),
            (
                self.resonance_proximity_percent,
                expected_proximity,
                "SPINDLE_HARMONIC_PROXIMITY_INCONSISTENT",
            ),
            (
                self.unbalance_force_n,
                expected_unbalance_force,
                "SPINDLE_HARMONIC_UNBALANCE_FORCE_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        if expected_proximity <= self.resonance_exclusion_percent:
            expected_status = "HARMONIC_RESONANCE_CRITICAL_RPM_WARNING"
        elif expected_unbalance_force > self.bearing_admissible_force_n:
            expected_status = "DYNAMIC_UNBALANCE_EXCESSIVE_FORCE_WARNING"
        else:
            expected_status = "SPINDLE_DYNAMICS_COMPLIANT"
        if self.dynamic_status != expected_status:
            raise ValueError("SPINDLE_HARMONIC_STATUS_INCONSISTENT")
        return self


class JawClampingPressureAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-jaw-clamping-pressure-audit/v1"] = (
        "vena-ia.cnc-jaw-clamping-pressure-audit/v1"
    )
    source_workholding_clamping_audit: WorkholdingClampingAuditPayload
    material_profile: Literal["AISI_1020", "ABNT_1045", "ALUMINUM_6061_T6"]
    jaw_count: Literal[3] = 3
    jaw_width_mm: float = Field(gt=0, le=10_000)
    effective_contact_length_mm: float = Field(gt=0, le=100_000)
    contact_area_mm2: float = Field(gt=0)
    dynamic_force_per_jaw_n: float = Field(gt=0)
    minimum_retention_pressure_mpa: float = Field(gt=0)
    mean_contact_pressure_mpa: float = Field(gt=0)
    material_yield_strength_mpa: float = Field(gt=0)
    pressure_ratio_percent: float = Field(gt=0)
    clamping_pressure_status: Literal[
        "JAW_SURFACE_INDENTATION_RISK_WARNING",
        "INSUFFICIENT_CLAMPING_PRESSURE_WARNING",
        "CLAMPING_PRESSURE_COMPLIANT",
    ]
    theoretical: Literal[True] = True
    physical: Literal[False] = False
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    automatic_chuck_pressure_control_authorized: Literal[False] = False
    model_limitation: Literal[
        "ESTIMATIVA ANALÍTICA DE PRESSÃO DE FIXAÇÃO - NÃO CONSIDERA SERRILHADOS, RAIOS DE CANTO OU DISTRIBUIÇÃO HERTZIANA NÃO LINEAR NAS CASTANHAS"
    ] = (
        "ESTIMATIVA ANALÍTICA DE PRESSÃO DE FIXAÇÃO - NÃO CONSIDERA SERRILHADOS, "
        "RAIOS DE CANTO OU DISTRIBUIÇÃO HERTZIANA NÃO LINEAR NAS CASTANHAS"
    )
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_jaw_contact_snapshot(self) -> "JawClampingPressureAuditPayload":
        workholding = self.source_workholding_clamping_audit
        expected_yield = {
            "AISI_1020": 250.0,
            "ABNT_1045": 350.0,
            "ALUMINUM_6061_T6": 276.0,
        }[self.material_profile]
        expected_area = self.jaw_width_mm * self.effective_contact_length_mm
        expected_force_per_jaw = workholding.dynamic_clamping_force_total_n / self.jaw_count
        expected_pressure = expected_force_per_jaw / expected_area
        expected_minimum_pressure = (
            workholding.required_safety_factor
            * workholding.axial_cutting_force_n
            / workholding.friction_coefficient
            / self.jaw_count
            / expected_area
        )
        expected_ratio = expected_pressure / expected_yield * 100.0
        comparisons = (
            (self.contact_area_mm2, expected_area, "JAW_CONTACT_AREA_INCONSISTENT"),
            (
                self.dynamic_force_per_jaw_n,
                expected_force_per_jaw,
                "JAW_CONTACT_FORCE_PER_JAW_INCONSISTENT",
            ),
            (
                self.minimum_retention_pressure_mpa,
                expected_minimum_pressure,
                "JAW_CONTACT_MINIMUM_RETENTION_PRESSURE_INCONSISTENT",
            ),
            (
                self.mean_contact_pressure_mpa,
                expected_pressure,
                "JAW_CONTACT_MEAN_PRESSURE_INCONSISTENT",
            ),
            (
                self.material_yield_strength_mpa,
                expected_yield,
                "JAW_CONTACT_YIELD_STRENGTH_INCONSISTENT",
            ),
            (
                self.pressure_ratio_percent,
                expected_ratio,
                "JAW_CONTACT_PRESSURE_RATIO_INCONSISTENT",
            ),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        if expected_pressure > 0.6 * expected_yield:
            expected_status = "JAW_SURFACE_INDENTATION_RISK_WARNING"
        elif expected_pressure < expected_minimum_pressure:
            expected_status = "INSUFFICIENT_CLAMPING_PRESSURE_WARNING"
        else:
            expected_status = "CLAMPING_PRESSURE_COMPLIANT"
        if self.clamping_pressure_status != expected_status:
            raise ValueError("JAW_CONTACT_PRESSURE_STATUS_INCONSISTENT")
        return self


class GuidewayLoadAuditPayload(_CNCGenerationContract):
    schema_version: Literal["vena-ia.cnc-guideway-load-audit/v1"] = (
        "vena-ia.cnc-guideway-load-audit/v1"
    )
    source_power_force_audit: MachiningPowerForceAuditPayload
    block_count: Literal[4] = 4
    feed_force_ratio: float = Field(gt=0, le=2.0)
    radial_force_ratio: float = Field(gt=0, le=2.0)
    tangential_cutting_force_n: float = Field(gt=0, le=10_000_000)
    axial_feed_force_n: float = Field(gt=0, le=10_000_000)
    radial_cutting_force_n: float = Field(gt=0, le=10_000_000)
    lever_arm_x_mm: float = Field(gt=0, le=100_000)
    lever_arm_y_mm: float = Field(gt=0, le=100_000)
    lever_arm_z_mm: float = Field(gt=0, le=100_000)
    block_spacing_x_mm: float = Field(gt=0, le=100_000)
    rail_spacing_y_mm: float = Field(gt=0, le=100_000)
    block_spacing_z_mm: float = Field(gt=0, le=100_000)
    pitching_moment_nm: float = Field(gt=0)
    yawing_moment_nm: float = Field(gt=0)
    rolling_moment_nm: float = Field(gt=0)
    direct_load_per_block_n: float = Field(gt=0)
    pitching_reaction_per_block_n: float = Field(gt=0)
    yawing_reaction_per_block_n: float = Field(gt=0)
    rolling_reaction_per_block_n: float = Field(gt=0)
    max_block_load_n: float = Field(gt=0)
    static_capacity_n: float = Field(gt=0, le=1_000_000_000)
    load_ratio_percent: float = Field(gt=0)
    guideway_status: Literal[
        "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING",
        "GUIDEWAY_LOAD_COMPLIANT",
    ]
    is_theoretical_model: Literal[True] = True
    physical_use_authorized: Literal[False] = False
    model_limitation: Literal[
        "ESTIMATIVA ANALÍTICA DE CARGA NOS GUIAS LINEARES - NÃO CONSIDERA PRÉ-CARGA INTERNA DOS PATINS, ERROS DE GEOMETRIA DO BARRAMENTO OU DESGASTE DE ESFERAS/ROLETES"
    ] = (
        "ESTIMATIVA ANALÍTICA DE CARGA NOS GUIAS LINEARES - NÃO CONSIDERA PRÉ-CARGA "
        "INTERNA DOS PATINS, ERROS DE GEOMETRIA DO BARRAMENTO OU DESGASTE DE "
        "ESFERAS/ROLETES"
    )
    safety_flags: GCodeSafetyFlags = Field(default_factory=GCodeSafetyFlags)

    @model_validator(mode="after")
    def validate_guideway_load_snapshot(self) -> "GuidewayLoadAuditPayload":
        tangential_force = self.source_power_force_audit.fc_nominal_n
        axial_force = tangential_force * self.feed_force_ratio
        radial_force = tangential_force * self.radial_force_ratio
        pitching_moment = (
            axial_force * self.lever_arm_z_mm
            + tangential_force * self.lever_arm_x_mm
        ) / 1_000.0
        yawing_moment = (
            axial_force * self.lever_arm_y_mm
            + radial_force * self.lever_arm_z_mm
        ) / 1_000.0
        rolling_moment = (
            radial_force * self.lever_arm_y_mm
            + tangential_force * self.lever_arm_z_mm
        ) / 1_000.0
        direct_load = math.sqrt(
            tangential_force**2 + axial_force**2 + radial_force**2
        ) / self.block_count
        pitching_reaction = (
            pitching_moment * 1_000.0 / (2.0 * self.block_spacing_z_mm)
        )
        yawing_reaction = (
            yawing_moment * 1_000.0 / (2.0 * self.block_spacing_x_mm)
        )
        rolling_reaction = (
            rolling_moment * 1_000.0 / (2.0 * self.rail_spacing_y_mm)
        )
        max_block_load = (
            direct_load + pitching_reaction + yawing_reaction + rolling_reaction
        )
        load_ratio = max_block_load / self.static_capacity_n * 100.0
        comparisons = (
            (
                self.tangential_cutting_force_n,
                tangential_force,
                "GUIDEWAY_TANGENTIAL_FORCE_INCONSISTENT",
            ),
            (self.axial_feed_force_n, axial_force, "GUIDEWAY_AXIAL_FORCE_INCONSISTENT"),
            (
                self.radial_cutting_force_n,
                radial_force,
                "GUIDEWAY_RADIAL_FORCE_INCONSISTENT",
            ),
            (self.pitching_moment_nm, pitching_moment, "GUIDEWAY_PITCHING_MOMENT_INCONSISTENT"),
            (self.yawing_moment_nm, yawing_moment, "GUIDEWAY_YAWING_MOMENT_INCONSISTENT"),
            (self.rolling_moment_nm, rolling_moment, "GUIDEWAY_ROLLING_MOMENT_INCONSISTENT"),
            (
                self.direct_load_per_block_n,
                direct_load,
                "GUIDEWAY_DIRECT_LOAD_INCONSISTENT",
            ),
            (
                self.pitching_reaction_per_block_n,
                pitching_reaction,
                "GUIDEWAY_PITCH_REACTION_INCONSISTENT",
            ),
            (
                self.yawing_reaction_per_block_n,
                yawing_reaction,
                "GUIDEWAY_YAW_REACTION_INCONSISTENT",
            ),
            (
                self.rolling_reaction_per_block_n,
                rolling_reaction,
                "GUIDEWAY_ROLL_REACTION_INCONSISTENT",
            ),
            (self.max_block_load_n, max_block_load, "GUIDEWAY_MAX_BLOCK_LOAD_INCONSISTENT"),
            (self.load_ratio_percent, load_ratio, "GUIDEWAY_LOAD_RATIO_INCONSISTENT"),
        )
        for actual, expected, code in comparisons:
            if not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12):
                raise ValueError(code)
        expected_status = (
            "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING"
            if max_block_load > 0.5 * self.static_capacity_n
            else "GUIDEWAY_LOAD_COMPLIANT"
        )
        if self.guideway_status != expected_status:
            raise ValueError("GUIDEWAY_STATUS_INCONSISTENT")
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
    tool_life_audits: tuple[ToolLifeTaylorAuditPayload, ...] = Field(min_length=1)
    tool_wear_geometry_audits: tuple[ToolWearGeometryAuditPayload, ...] = Field(
        min_length=1
    )
    cost_time_audit: MachiningCostTimeAuditPayload
    sustainability_audit: MachiningSustainabilityAuditPayload
    stability_audits: tuple[MachiningStabilityAuditPayload, ...] = Field(min_length=1)
    parameter_optimizations: tuple[MachiningParameterOptimizationPayload, ...] = Field(min_length=1)
    risk_matrix: MachiningRiskMatrixPayload
    process_sheet: MachiningProcessSheetPayload
    residual_stock_audit: MachiningResidualStockAuditPayload
    part_elastic_deflection_audit: PartElasticDeflectionAuditPayload
    spindle_power_torque_envelope_audit: SpindlePowerTorqueEnvelopeAuditPayload
    thermal_expansion_drift_audit: ThermalExpansionDriftAuditPayload
    chip_breaking_machinability_audit: ChipBreakingMachinabilityAuditPayload
    coolant_pressure_flow_audit: CoolantPressureFlowAuditPayload
    workholding_clamping_audit: WorkholdingClampingAuditPayload
    tailstock_thrust_audit: TailstockThrustAuditPayload
    spindle_harmonic_dynamics_audit: SpindleHarmonicDynamicsAuditPayload
    jaw_clamping_pressure_audit: JawClampingPressureAuditPayload
    guideway_load_audit: GuidewayLoadAuditPayload
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
        if not math.isclose(
            self.cost_time_audit.cutting_time_minutes,
            self.cycle_time_estimate.total_cutting_time_seconds / 60,
            abs_tol=5e-9,
        ) or not math.isclose(
            self.cost_time_audit.rapid_time_minutes,
            self.cycle_time_estimate.total_rapid_time_seconds / 60,
            abs_tol=5e-9,
        ):
            raise ValueError("REPORT_COST_TIME_SOURCE_INCONSISTENT")
        lives_by_tool = {item.tool_id: item for item in self.tool_life_audits}
        if len(lives_by_tool) != len(self.tool_life_audits):
            raise ValueError("REPORT_TOOL_LIFE_DUPLICATE")
        wear_by_tool = {
            item.source_tool_life_audit.tool_id: item
            for item in self.tool_wear_geometry_audits
        }
        if (
            len(wear_by_tool) != len(self.tool_wear_geometry_audits)
            or set(wear_by_tool) != set(lives_by_tool)
            or any(
                item.source_tool_life_audit != lives_by_tool[tool_id]
                for tool_id, item in wear_by_tool.items()
            )
        ):
            raise ValueError("REPORT_TOOL_WEAR_GEOMETRY_SOURCE_INCONSISTENT")
        if {item.tool_id for item in self.cost_time_audit.per_tool_wear_costs} != set(
            lives_by_tool
        ):
            raise ValueError("REPORT_TOOLING_COST_SOURCE_INCONSISTENT")
        for cost in self.cost_time_audit.per_tool_wear_costs:
            life = lives_by_tool[cost.tool_id]
            if not math.isclose(
                cost.effective_cutting_time_minutes,
                life.effective_cutting_time_minutes,
                abs_tol=5e-9,
            ) or not math.isclose(
                cost.estimated_tool_life_minutes,
                life.estimated_tool_life_minutes,
                abs_tol=5e-9,
            ):
                raise ValueError("REPORT_TOOLING_COST_SOURCE_INCONSISTENT")
        if not math.isclose(
            self.sustainability_audit.motor_power_kw,
            self.power_force_audit.p_motor_est_kw,
            abs_tol=5e-9,
        ) or not math.isclose(
            self.sustainability_audit.cutting_time_minutes,
            self.cost_time_audit.cutting_time_minutes,
            abs_tol=5e-9,
        ) or not math.isclose(
            self.sustainability_audit.total_cycle_time_minutes,
            self.cost_time_audit.total_cycle_time_minutes,
            abs_tol=5e-9,
        ):
            raise ValueError("REPORT_SUSTAINABILITY_SOURCE_INCONSISTENT")
        stability_by_tool = {item.tool_id: item for item in self.stability_audits}
        if len(stability_by_tool) != len(self.stability_audits) or set(stability_by_tool) != {
            item.tool_id for item in self.tools
        }:
            raise ValueError("REPORT_STABILITY_TOOL_SOURCE_INCONSISTENT")
        for stability in self.stability_audits:
            if not math.isclose(
                stability.cutting_force_n,
                self.power_force_audit.fc_nominal_n,
                abs_tol=5e-9,
            ) or not math.isclose(
                stability.specific_cutting_pressure_n_per_mm2,
                self.power_force_audit.kc1_1_n_per_mm2,
                abs_tol=5e-9,
            ) or not math.isclose(
                stability.depth_of_cut_mm,
                self.power_force_audit.depth_of_cut_mm,
                abs_tol=5e-9,
            ):
                raise ValueError("REPORT_STABILITY_SOURCE_INCONSISTENT")
        optimizations_by_tool = {item.tool_id: item for item in self.parameter_optimizations}
        if len(optimizations_by_tool) != len(self.parameter_optimizations) or set(
            optimizations_by_tool
        ) != set(stability_by_tool):
            raise ValueError("REPORT_OPTIMIZATION_TOOL_SOURCE_INCONSISTENT")
        for optimization in self.parameter_optimizations:
            stability = stability_by_tool[optimization.tool_id]
            roughness_target = (
                self.surface_roughness_audit.nominal_ra_max_um
                or self.surface_roughness_audit.ra_theoretical_um
            )
            comparisons = (
                (optimization.programmed_vc_m_min, self.power_force_audit.cutting_speed_m_per_min),
                (optimization.programmed_feed_mm_rev, self.power_force_audit.feed_mm_per_rev),
                (optimization.programmed_ap_mm, self.power_force_audit.depth_of_cut_mm),
                (optimization.target_ra_um, roughness_target),
                (optimization.insert_nose_radius_mm, self.surface_roughness_audit.insert_nose_radius_mm),
                (optimization.cutting_edge_angle_deg, self.power_force_audit.cutting_edge_angle_deg),
                (optimization.machine_power_limit_kw, self.power_force_audit.machine_power_limit_kw),
                (optimization.stability_limit_depth_mm, stability.stability_limit_depth_mm),
                (optimization.overhang_ratio_l_d, stability.overhang_ratio_l_d),
            )
            if optimization.material_profile != self.power_force_audit.material_profile or any(
                not math.isclose(actual, expected, abs_tol=5e-9)
                for actual, expected in comparisons
            ):
                raise ValueError("REPORT_OPTIMIZATION_SOURCE_INCONSISTENT")
        risk = self.risk_matrix
        max_overhang_ratio = max(item.overhang_ratio_l_d for item in self.stability_audits)
        dynamic_warning = any(
            item.stability_status == "CHATTER_HIGH_RISK_WARNING"
            for item in self.stability_audits
        )
        max_wear = max(item.tool_life_consumed_percent for item in self.tool_life_audits)
        wear_warning = any(
            item.integrity_status == "TOOL_LIFE_EXHAUSTED_WARNING"
            for item in self.tool_life_audits
        )
        risk_comparisons = (
            (risk.minimum_chuck_clearance_mm, self.chuck_proximity.minimum_clearance_mm),
            (risk.chuck_proximity_threshold_mm, self.chuck_proximity.threshold_mm),
            (risk.max_overhang_ratio_l_d, max_overhang_ratio),
            (risk.required_motor_power_kw, self.power_force_audit.p_motor_est_kw),
            (risk.machine_power_limit_kw, self.power_force_audit.machine_power_limit_kw),
            (risk.max_tool_life_consumed_percent, max_wear),
        )
        if (
            risk.envelope_audit != self.envelope_audit
            or risk.geometry_audit_status != self.geometry_audit.status
            or risk.geometry_manifest_generation_allowed
            != self.geometry_audit.manifest_generation_allowed
            or risk.chuck_proximity_warning
            != (self.chuck_proximity.warning_code == "WARNING_PROXIMITY_CHUCK")
            or risk.dynamic_warning_present != dynamic_warning
            or risk.power_warning_present
            != (self.power_force_audit.power_status == "POWER_EXCEEDED_WARNING")
            or risk.tool_wear_warning_present != wear_warning
            or any(
                not math.isclose(actual, expected, abs_tol=5e-9)
                for actual, expected in risk_comparisons
            )
        ):
            raise ValueError("REPORT_RISK_MATRIX_SOURCE_INCONSISTENT")
        sheet = self.process_sheet
        if (
            sheet.part_id != self.cad_job_id
            or sheet.source_plan_id != self.plan_id
            or sheet.source_cycle_time_estimate != self.cycle_time_estimate
            or sheet.source_machine_envelope != self.machine_envelope
            or sheet.source_chuck_proximity != self.chuck_proximity
            or {item.tool_id for item in sheet.sequence_operations[1:]}
            != {item.tool_id for item in self.tools}
            or {item.phase for item in sheet.sequence_operations[1:]}
            != {operation.value for item in self.tools for operation in item.operations}
        ):
            raise ValueError("REPORT_PROCESS_SHEET_SOURCE_INCONSISTENT")
        for step in sheet.sequence_operations[1:]:
            if (
                not math.isclose(
                    step.cutting_speed_vc_m_per_min or 0,
                    self.power_force_audit.cutting_speed_m_per_min,
                    abs_tol=5e-9,
                )
                or not math.isclose(
                    step.feed_mm_per_rev or 0,
                    self.power_force_audit.feed_mm_per_rev,
                    abs_tol=5e-9,
                )
                or not math.isclose(
                    step.depth_of_cut_ap_mm or 0,
                    self.power_force_audit.depth_of_cut_mm,
                    abs_tol=5e-9,
                )
            ):
                raise ValueError("REPORT_PROCESS_SHEET_PARAMETERS_INCONSISTENT")
        residual = self.residual_stock_audit
        nominal_radius = max(point.r_mm for point in residual.source_nominal_profile)
        nominal_min_z = min(point.z_mm for point in residual.source_nominal_profile)
        nominal_max_z = max(point.z_mm for point in residual.source_nominal_profile)
        geometry_by_axis = {item.axis: item for item in self.geometry_audit.deviations}
        if (
            residual.source_plan_id != self.plan_id
            or residual.source_cam_plan != sheet.source_cam_plan
            or not math.isclose(
                residual.stock_radius_mm,
                sheet.source_stock.diameter_mm / 2.0,
                abs_tol=5e-9,
            )
            or not math.isclose(
                nominal_radius, geometry_by_axis["MAX_RADIUS"].nominal_mm, abs_tol=5e-9
            )
            or not math.isclose(nominal_min_z, geometry_by_axis["MIN_Z"].nominal_mm, abs_tol=5e-9)
            or not math.isclose(nominal_max_z, geometry_by_axis["MAX_Z"].nominal_mm, abs_tol=5e-9)
        ):
            raise ValueError("REPORT_RESIDUAL_STOCK_SOURCE_INCONSISTENT")
        deflection = self.part_elastic_deflection_audit
        positive_nominal_radii = tuple(
            point.r_mm
            for point in residual.source_nominal_profile
            if point.r_mm > residual.linear_tolerance_mm
        )
        expected_minimum_diameter = min(positive_nominal_radii) * 2.0
        expected_unsupported_length = nominal_max_z - nominal_min_z
        expected_young_modulus = {
            "AISI_1020": 210_000.0,
            "ABNT_1045": 210_000.0,
            "ALUMINUM_6061_T6": 69_000.0,
        }[self.power_force_audit.material_profile]
        deflection_sources = (
            (deflection.part_unsupported_length_mm, expected_unsupported_length),
            (deflection.minimum_diameter_mm, expected_minimum_diameter),
            (deflection.radial_cutting_force_n, self.power_force_audit.fc_nominal_n * 0.5),
            (deflection.young_modulus_mpa, expected_young_modulus),
        )
        if any(
            not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12)
            for actual, expected in deflection_sources
        ):
            raise ValueError("REPORT_PART_DEFLECTION_SOURCE_INCONSISTENT")
        spindle = self.spindle_power_torque_envelope_audit
        if spindle.source_power_force_audit != self.power_force_audit or not any(
            math.isclose(
                point.spindle_rpm,
                self.power_force_audit.spindle_rpm_reference,
                abs_tol=5e-9,
            )
            for point in spindle.operating_points
        ):
            raise ValueError("REPORT_SPINDLE_ENVELOPE_SOURCE_INCONSISTENT")
        thermal = self.thermal_expansion_drift_audit
        if thermal.material_profile != self.power_force_audit.material_profile:
            raise ValueError("REPORT_THERMAL_DRIFT_SOURCE_INCONSISTENT")
        chip_breaking = self.chip_breaking_machinability_audit
        chip_breaking_sources = (
            (chip_breaking.feed_mm_per_rev, self.power_force_audit.feed_mm_per_rev),
            (chip_breaking.depth_of_cut_mm, self.power_force_audit.depth_of_cut_mm),
            (
                chip_breaking.cutting_edge_angle_deg,
                self.power_force_audit.cutting_edge_angle_deg,
            ),
            (
                chip_breaking.uncut_chip_thickness_mm,
                self.power_force_audit.chip_thickness_mm,
            ),
            (chip_breaking.chip_width_mm, self.power_force_audit.chip_width_mm),
        )
        if chip_breaking.material_profile != self.power_force_audit.material_profile or any(
            not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12)
            for actual, expected in chip_breaking_sources
        ):
            raise ValueError("REPORT_CHIP_BREAKING_SOURCE_INCONSISTENT")
        if self.coolant_pressure_flow_audit.safety_flags != self.safety_flags:
            raise ValueError("REPORT_COOLANT_SAFETY_FLAGS_INCONSISTENT")
        workholding = self.workholding_clamping_audit
        if workholding.safety_flags != self.safety_flags:
            raise ValueError("REPORT_WORKHOLDING_SAFETY_FLAGS_INCONSISTENT")
        if not math.isclose(
            workholding.axial_cutting_force_n,
            self.power_force_audit.fc_nominal_n,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ) or not math.isclose(
            workholding.operating_rpm,
            self.power_force_audit.spindle_rpm_reference,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ) or not math.isclose(
            workholding.maximum_declared_rpm,
            self.power_force_audit.max_spindle_rpm,
            abs_tol=5e-9,
            rel_tol=1e-12,
        ):
            raise ValueError("REPORT_WORKHOLDING_SOURCE_INCONSISTENT")
        tailstock = self.tailstock_thrust_audit
        tailstock_sources = (
            (
                tailstock.radial_cutting_force_n,
                self.power_force_audit.fc_nominal_n * 0.5,
            ),
            (
                tailstock.total_supported_length_mm,
                self.part_elastic_deflection_audit.part_unsupported_length_mm,
            ),
            (
                tailstock.minimum_diameter_mm,
                self.part_elastic_deflection_audit.minimum_diameter_mm,
            ),
            (
                tailstock.young_modulus_mpa,
                self.part_elastic_deflection_audit.young_modulus_mpa,
            ),
            (tailstock.engagement_z_coordinate_mm, nominal_max_z),
        )
        if (
            tailstock.safety_flags != self.safety_flags
            or any(
                not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12)
                for actual, expected in tailstock_sources
            )
        ):
            raise ValueError("REPORT_TAILSTOCK_SOURCE_INCONSISTENT")
        harmonic = self.spindle_harmonic_dynamics_audit
        density_by_material = {
            "AISI_1020": 7_850.0,
            "ABNT_1045": 7_850.0,
            "ALUMINUM_6061_T6": 2_700.0,
        }
        density = density_by_material[self.power_force_audit.material_profile]
        radius_m = self.part_elastic_deflection_audit.minimum_diameter_mm / 2_000.0
        expected_workpiece_mass = (
            density
            * math.pi
            * radius_m**2
            * (self.part_elastic_deflection_audit.part_unsupported_length_mm / 1_000.0)
        )
        harmonic_sources = (
            (
                harmonic.system_stiffness_n_per_m,
                self.part_elastic_deflection_audit.calculated_stiffness_n_per_mm * 1_000.0,
            ),
            (harmonic.workpiece_mass_kg, expected_workpiece_mass),
            (harmonic.effective_mass_kg, expected_workpiece_mass * 0.236),
            (harmonic.operating_rpm, self.power_force_audit.spindle_rpm_reference),
        )
        if (
            harmonic.safety_flags != self.safety_flags
            or any(
                not math.isclose(actual, expected, abs_tol=5e-9, rel_tol=1e-12)
                for actual, expected in harmonic_sources
            )
        ):
            raise ValueError("REPORT_SPINDLE_HARMONIC_SOURCE_INCONSISTENT")
        jaw_pressure = self.jaw_clamping_pressure_audit
        if (
            jaw_pressure.safety_flags != self.safety_flags
            or jaw_pressure.source_workholding_clamping_audit != workholding
            or jaw_pressure.material_profile != self.power_force_audit.material_profile
        ):
            raise ValueError("REPORT_JAW_CONTACT_PRESSURE_SOURCE_INCONSISTENT")
        guideway = self.guideway_load_audit
        if (
            guideway.safety_flags != self.safety_flags
            or guideway.source_power_force_audit != self.power_force_audit
        ):
            raise ValueError("REPORT_GUIDEWAY_LOAD_SOURCE_INCONSISTENT")
        return self
