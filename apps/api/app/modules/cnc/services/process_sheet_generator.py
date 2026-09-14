"""Deterministic, review-only CNC process routing sheet synthesis."""

from math import fsum

from app.modules.cam.schemas import TurningStrategyPlanResponse
from app.modules.cnc.schemas import (
    ChuckProximityAudit,
    CycleTimeEstimatePayload,
    MachineEnvelope2D,
    MachiningProcessSheetPayload,
    OperationStep,
    ProcessSheetClampingSetup,
    RawStockDimensions,
    TurningStock2D,
)


class ProcessSheetGenerationError(ValueError):
    """Stable fail-closed error for inconsistent process-sheet sources."""


PROCESS_SHEET_NOTE = (
    "FOLHA DE PROCESSO TEÓRICA ANALÍTICA - DOCUMENTO ORIENTATIVO SUJEITO À "
    "APROVAÇÃO DO PREPARADOR DE MÁQUINAS"
)

SAFETY_INSTRUCTIONS = (
    "Confirmar manualmente a fixação, a projeção do material e a folga em relação à placa.",
    "Conferir ferramenta, inserto, corretores e parâmetros com a engenharia de processos.",
    "Submeter a folha ao preparador de máquinas; este documento não concede permissão física.",
)


def _allocated_times(
    plan: TurningStrategyPlanResponse,
    total_cycle_time_min: float,
) -> tuple[float, ...]:
    volumes = tuple(item.estimated_removed_volume_mm3 for item in plan.passes)
    total_volume = fsum(volumes)
    weights = (
        tuple(value / total_volume for value in volumes)
        if total_volume > 0
        else tuple(1.0 / len(volumes) for _ in volumes)
    )
    allocated: list[float] = []
    consumed = 0.0
    for index, weight in enumerate(weights):
        value = (
            total_cycle_time_min - consumed
            if index == len(weights) - 1
            else total_cycle_time_min * weight
        )
        allocated.append(value)
        consumed += value
    return tuple(allocated)


def generate_process_sheet(
    *,
    part_id: str,
    revision: str,
    source_plan_id: str,
    cam_plan: TurningStrategyPlanResponse,
    stock: TurningStock2D,
    machine_envelope: MachineEnvelope2D,
    chuck_proximity: ChuckProximityAudit,
    cycle_time_estimate: CycleTimeEstimatePayload,
    tool_id: str,
    tool_description: str,
    insert_nose_radius_mm: float,
    tool_orientation: str,
    cutting_speed_vc_m_per_min: float,
    feed_mm_per_rev: float,
    depth_of_cut_ap_mm: float,
    spindle_rpm: float,
    setup_time_min: float = 15.0,
) -> MachiningProcessSheetPayload:
    """Compile CAM and analytical snapshots into a non-executable routing sheet."""
    validated_plan = TurningStrategyPlanResponse.model_validate(cam_plan)
    validated_stock = TurningStock2D.model_validate(stock)
    validated_envelope = MachineEnvelope2D.model_validate(machine_envelope)
    validated_proximity = ChuckProximityAudit.model_validate(chuck_proximity)
    validated_cycle = CycleTimeEstimatePayload.model_validate(cycle_time_estimate)
    if tuple(item.sequence for item in validated_plan.passes) != tuple(
        range(1, len(validated_plan.passes) + 1)
    ):
        raise ProcessSheetGenerationError("PROCESS_SHEET_CAM_SEQUENCE_INVALID")
    if any(
        item.operation_type != validated_plan.operation_type
        for item in validated_plan.passes
    ):
        raise ProcessSheetGenerationError("PROCESS_SHEET_CAM_OPERATION_INCONSISTENT")
    if (
        setup_time_min <= 0
        or cutting_speed_vc_m_per_min <= 0
        or feed_mm_per_rev <= 0
        or depth_of_cut_ap_mm <= 0
        or spindle_rpm <= 0
    ):
        raise ProcessSheetGenerationError("PROCESS_SHEET_PARAMETERS_INVALID")
    if (
        validated_stock.diameter_mm > validated_envelope.x_max_mm
        or validated_stock.z_min_mm < validated_envelope.z_min_mm
        or validated_stock.z_max_mm > validated_envelope.z_max_mm
        or validated_proximity.minimum_clearance_mm <= 0
    ):
        raise ProcessSheetGenerationError("PROCESS_SHEET_CLAMPING_INVALID")
    source_tools = {item.tool for item in validated_cycle.per_tool_breakdown}
    if not source_tools or source_tools != {tool_id}:
        raise ProcessSheetGenerationError("PROCESS_SHEET_TOOL_SOURCE_INCONSISTENT")

    total_cycle_time_min = validated_cycle.total_cycle_time_seconds / 60.0
    phase_times = _allocated_times(validated_plan, total_cycle_time_min)
    feed_rate_mm_min = feed_mm_per_rev * spindle_rpm
    insert_reference = (
        f"INSERT_R{insert_nose_radius_mm:.3f}_{tool_orientation}"
    )
    operations: list[OperationStep] = [
        OperationStep(
            sequence=1,
            operation_id="OP010",
            phase="SETUP",
            estimated_time_min=setup_time_min,
        )
    ]
    operations.extend(
        OperationStep(
            sequence=index + 2,
            operation_id=f"OP{(index + 2) * 10:03d}",
            phase=source.operation_type.value,
            source_pass_sequence=source.sequence,
            tool_id=tool_id,
            tool_description=tool_description,
            insert_reference=insert_reference,
            cutting_speed_vc_m_per_min=cutting_speed_vc_m_per_min,
            feed_mm_per_rev=feed_mm_per_rev,
            depth_of_cut_ap_mm=depth_of_cut_ap_mm,
            spindle_rpm=spindle_rpm,
            feed_rate_mm_min=feed_rate_mm_min,
            estimated_time_min=phase_times[index],
        )
        for index, source in enumerate(validated_plan.passes)
    )
    return MachiningProcessSheetPayload(
        part_id=part_id,
        revision=revision,
        source_plan_id=source_plan_id,
        source_cam_plan=validated_plan,
        source_stock=validated_stock,
        source_machine_envelope=validated_envelope,
        source_chuck_proximity=validated_proximity,
        source_cycle_time_estimate=validated_cycle,
        raw_stock_dimensions=RawStockDimensions(
            diameter_mm=validated_stock.diameter_mm,
            axial_length_mm=validated_stock.z_max_mm - validated_stock.z_min_mm,
            z_min_mm=validated_stock.z_min_mm,
            z_max_mm=validated_stock.z_max_mm,
        ),
        clamping_setup=ProcessSheetClampingSetup(
            chuck_exclusion_zone=validated_envelope.chuck_exclusion_zone,
            minimum_clearance_mm=validated_proximity.minimum_clearance_mm,
            proximity_threshold_mm=validated_proximity.threshold_mm,
            estimated_setup_time_min=setup_time_min,
        ),
        sequence_operations=tuple(operations),
        total_operations_count=len(operations),
        estimated_total_time_min=setup_time_min + total_cycle_time_min,
        safety_instructions=SAFETY_INSTRUCTIONS,
    )


__all__ = (
    "PROCESS_SHEET_NOTE",
    "ProcessSheetGenerationError",
    "SAFETY_INSTRUCTIONS",
    "generate_process_sheet",
)
