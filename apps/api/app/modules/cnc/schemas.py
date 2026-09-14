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
    cost_time_audit: MachiningCostTimeAuditPayload
    sustainability_audit: MachiningSustainabilityAuditPayload
    stability_audits: tuple[MachiningStabilityAuditPayload, ...] = Field(min_length=1)
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
        return self
