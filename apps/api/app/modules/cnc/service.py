from app.modules.cnc.schemas import CNCPlanPreview, CNCPlanRequest
from app.modules.engineering.schemas import FeaturePlanningResponse


class CNCPlanningService:
    """Builds a neutral, non-executable plan for later post-processing."""

    def preview(self, request: CNCPlanRequest) -> CNCPlanPreview:
        return CNCPlanPreview(
            controller_family="FANUC_OI_STRATEGY_PLACEHOLDER",
            machine_profile="ROMI_D1250_PLANNED_COMPATIBILITY",
            operation=request.operation,
            parameters={
                "tool_number": request.tool_number,
                "spindle_rpm": request.spindle_rpm,
                "feed_mm_min": request.feed_mm_min,
                "clearance_z_mm": request.clearance_z_mm,
            },
            machine_neutral_assumptions=[
                "Controller family and machine profile are planning placeholders only.",
                "Clearance is an explicit preliminary input, not a verified toolpath coordinate.",
            ],
            validation_checks=[
                "POSITIVE_CLEARANCE",
                "RPM_WITHIN_PRELIMINARY_SCHEMA_LIMIT",
                "FEED_WITHIN_PRELIMINARY_SCHEMA_LIMIT",
                "TOOL_IDENTIFIER_PRESENT",
            ],
            status="SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW",
            warnings=["Human review is mandatory before any downstream use."],
            traceability=["cnc-preview-rule:1.0.0"],
            limitations=[
                "No G-code or controller blocks are generated.",
                "No collision, fixture, stock, kinematic or physical validation.",
                "Not approved for machine transmission or production.",
            ],
        )

    def neutral_plan(
        self,
        request: CNCPlanRequest,
        planning: FeaturePlanningResponse,
        *,
        planning_reference: str,
        recommendation_reference: str | None,
    ) -> CNCPlanPreview:
        preview = self.preview(request)
        return preview.model_copy(
            update={
                "source_planning_reference": planning_reference,
                "source_recommendation_reference": recommendation_reference,
                "operation_candidates": [
                    candidate.model_dump(mode="json")
                    for candidate in planning.planning_candidates
                ],
                "traceability": [
                    *preview.traceability,
                    planning_reference,
                    *(planning.traceability),
                    *([] if recommendation_reference is None else [recommendation_reference]),
                ],
            }
        )
