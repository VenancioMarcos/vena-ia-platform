from app.modules.cnc.schemas import CNCPlanPreview, CNCPlanRequest


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
            validation_checks=[
                "POSITIVE_CLEARANCE",
                "RPM_WITHIN_PRELIMINARY_SCHEMA_LIMIT",
                "FEED_WITHIN_PRELIMINARY_SCHEMA_LIMIT",
                "TOOL_IDENTIFIER_PRESENT",
            ],
            status="SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW",
            executable_output=False,
            limitations=[
                "No G-code or controller blocks are generated.",
                "No collision, fixture, stock, kinematic or physical validation.",
                "Not approved for machine transmission or production.",
            ],
        )
