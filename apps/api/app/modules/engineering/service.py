import math
from typing import cast

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.modules.engineering.models import EngineeringCatalogItem
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.schemas import (
    CatalogItemCreate,
    CatalogItemRead,
    CatalogDeletionStatus,
    CatalogGovernanceEvidence,
    CatalogGovernanceReference,
    CatalogKind,
    CatalogLifecycle,
    CatalogReconciliationStatus,
    CatalogRetentionStatus,
    CatalogScope,
    EngineeringRecommendation,
    EngineeringReviewReport,
    AvailabilityValue,
    PreliminarySelection,
    SelectionRequest,
    RecommendationRequest,
    ReviewChecklistItem,
)
from app.modules.organizations.schemas import OrganizationRole
from app.modules.organizations.service import OrganizationAuthorization


class EngineeringCatalogService:
    def __init__(
        self,
        repository: EngineeringCatalogRepository,
        authorization: OrganizationAuthorization,
    ) -> None:
        self.repository = repository
        self.authorization = authorization

    def create(
        self, payload: CatalogItemCreate, user_id: str, organization_id: str
    ) -> EngineeringCatalogItem:
        self.authorization.require_role(
            organization_id, {OrganizationRole.OWNER, OrganizationRole.ADMIN}
        )
        try:
            return self.repository.add(
                EngineeringCatalogItem(
                    **payload.model_dump(mode="json"),
                    created_by=user_id,
                    organization_id=organization_id,
                    scope_type=CatalogScope.ORGANIZATION_OWNED.value,
                )
            )
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise HTTPException(status_code=409, detail="Catalog item already exists") from exc

    def list(
        self, *, organization_id: str | None, kind: CatalogKind | None
    ) -> list[EngineeringCatalogItem]:
        if organization_id is not None:
            self.authorization.require_organization(organization_id)
        return self.repository.list_accessible(
            organization_id=organization_id,
            kind=kind.value if kind is not None else None,
        )

    def _get_authorized(self, item_id: str, kind: CatalogKind) -> EngineeringCatalogItem:
        item = self._get_authorized_item(item_id)
        if item.kind != kind.value:
            raise HTTPException(
                status_code=404, detail=f"{kind.value.title()} catalog item not found"
            )
        return item

    def _get_authorized_item(self, item_id: str) -> EngineeringCatalogItem:
        item = self.repository.get(item_id)
        if item is None or item.scope_type == "LEGACY_UNSCOPED":
            raise HTTPException(status_code=404, detail="Catalog item not found")
        if item.scope_type == "ORGANIZATION_OWNED":
            if item.organization_id is None:
                raise HTTPException(status_code=404, detail="Catalog item not found")
            self.authorization.require_organization(item.organization_id)
        elif item.scope_type != "SYSTEM_REFERENCE":
            raise HTTPException(status_code=404, detail="Catalog item not found")
        return item

    def governance(self, item_id: str) -> CatalogGovernanceEvidence:
        item = self._get_authorized_item(item_id)
        is_system = item.scope_type == CatalogScope.SYSTEM_REFERENCE.value
        return CatalogGovernanceEvidence(
            catalog_reference=CatalogGovernanceReference(
                id=item.id,
                kind=CatalogKind(item.kind),
                code=item.code,
                data_version=item.data_version,
            ),
            scope_type=CatalogScope(item.scope_type),
            organization_reference=item.organization_id,
            provenance=item.source,
            created_at=item.created_at,
            created_by=item.created_by,
            lifecycle_status=(
                CatalogLifecycle.SYSTEM_READ_ONLY if is_system else CatalogLifecycle.ACTIVE
            ),
            audit_references=([] if is_system else ["event-type:ENGINEERING_CATALOG_CREATED"]),
            retention_status=(
                CatalogRetentionStatus.SYSTEM_MANAGED_NO_TENANT_POLICY
                if is_system
                else CatalogRetentionStatus.RETAINED_FOR_TRACEABILITY_NO_TEMPORAL_POLICY
            ),
            deletion_status=(
                CatalogDeletionStatus.SYSTEM_MUTATION_NOT_EXPOSED
                if is_system
                else CatalogDeletionStatus.DELETE_NOT_EXPOSED
            ),
            reconciliation_status=(
                CatalogReconciliationStatus.SYSTEM_REFERENCE_NOT_RECONCILABLE
                if is_system
                else CatalogReconciliationStatus.NOT_APPLICABLE
            ),
            limitations=[
                "Evidence is an authorized read model, not production readiness or approval.",
                "No temporal retention or deletion endpoint is defined in v2.1.",
            ],
            warnings=(
                []
                if is_system
                else [
                    "Audit references identify the event class; the existing audit schema "
                    "does not claim a resource-level event link."
                ]
            ),
        )

    def select(self, payload: SelectionRequest) -> PreliminarySelection:
        expected = (
            (payload.material_id, CatalogKind.MATERIAL),
            (payload.machine_id, CatalogKind.MACHINE),
            (payload.tool_id, CatalogKind.TOOL),
        )
        items: list[EngineeringCatalogItem] = []
        for item_id, kind in expected:
            item = self._get_authorized(item_id, kind)
            items.append(item)
        organization_ids = {
            item.organization_id for item in items if item.scope_type == "ORGANIZATION_OWNED"
        }
        if len(organization_ids) > 1:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        material, machine, tool = items
        return PreliminarySelection(
            operation=payload.operation,
            material=CatalogItemRead.model_validate(material),
            machine=CatalogItemRead.model_validate(machine),
            tool=CatalogItemRead.model_validate(tool),
            traceability=[
                f"{item.scope_type}:{item.kind}:{item.code}@{item.data_version}:{item.source}"
                for item in items
            ],
            limitations=[
                "No toolpath or executable G-code is generated.",
                "Compatibility and process limits require qualified human validation.",
            ],
        )

    def recommend(self, payload: RecommendationRequest) -> EngineeringRecommendation:
        selection = self.select(payload)
        operation = payload.operation.lower()
        if operation not in {"milling", "drilling", "turning"}:
            raise HTTPException(status_code=422, detail="Operation is not allowlisted")

        props = [
            selection.material.properties,
            selection.machine.properties,
            selection.tool.properties,
        ]
        supported = [item.get("operations") for item in props[1:]]
        if any(not isinstance(values, list) or operation not in values for values in supported):
            compatibility = "PRELIMINARY_COMPATIBILITY_CHECK:INCOMPATIBLE"
        else:
            compatibility = "PRELIMINARY_COMPATIBILITY_CHECK:COMPATIBLE"

        required = {
            "cutting_speed_m_min": props[0].get("cutting_speed_m_min"),
            "feed_per_tooth_mm": props[0].get("feed_per_tooth_mm"),
            "max_rpm": props[1].get("max_rpm"),
            "max_feed_mm_min": props[1].get("max_feed_mm_min"),
            "diameter_mm": props[2].get("diameter_mm"),
            "teeth": props[2].get("teeth"),
        }
        missing = [
            key
            for key, value in required.items()
            if not isinstance(value, (int, float)) or value <= 0
        ]
        unavailable = AvailabilityValue(
            status="NOT_AVAILABLE", reason="Missing or invalid: " + ", ".join(missing)
        )
        parameters: dict[str, AvailabilityValue] = {
            "spindle_speed": unavailable,
            "feed_rate": unavailable,
        }
        formulas: list[str] = []
        feed = None
        if not missing and compatibility.endswith("COMPATIBLE"):
            numeric = {key: float(cast(int | float, value)) for key, value in required.items()}
            rpm = min(
                1000 * numeric["cutting_speed_m_min"] / (math.pi * numeric["diameter_mm"]),
                numeric["max_rpm"],
            )
            feed = min(
                rpm * numeric["teeth"] * numeric["feed_per_tooth_mm"],
                numeric["max_feed_mm_min"],
            )
            parameters = {
                "spindle_speed": AvailabilityValue(
                    status="AVAILABLE", value=round(rpm, 2), unit="rpm"
                ),
                "feed_rate": AvailabilityValue(
                    status="AVAILABLE", value=round(feed, 2), unit="mm/min"
                ),
            }
            formulas = [
                "rpm = min(1000 * cutting_speed_m_min / (pi * diameter_mm), max_rpm)",
                "feed_mm_min = min(rpm * teeth * feed_per_tooth_mm, max_feed_mm_min)",
            ]

        machining = AvailabilityValue(
            status="NOT_AVAILABLE", reason="cutting_length_mm and compatible feed are required"
        )
        if payload.cutting_length_mm is not None and feed:
            machining = AvailabilityValue(
                status="AVAILABLE", value=round(payload.cutting_length_mm / feed, 3), unit="min"
            )
        setup = (
            AvailabilityValue(
                status="AVAILABLE", value=round(payload.setup_time_min, 3), unit="min"
            )
            if payload.setup_time_min is not None
            else AvailabilityValue(status="NOT_AVAILABLE", reason="setup_time_min was not supplied")
        )
        total = AvailabilityValue(
            status="NOT_AVAILABLE", reason="machining and setup time are required"
        )
        if machining.value is not None and setup.value is not None:
            total = AvailabilityValue(
                status="AVAILABLE", value=round(machining.value + setup.value, 3), unit="min"
            )

        components: dict[str, float] = {}
        cost = AvailabilityValue(
            status="NOT_AVAILABLE", reason="currency, machine_hour_rate and total time are required"
        )
        if payload.currency and payload.machine_hour_rate is not None and total.value is not None:
            components = {
                "machine": round(total.value / 60 * payload.machine_hour_rate, 2),
                "tool": round(payload.tool_cost_allocation or 0, 2),
                "consumable": round(payload.consumable_cost or 0, 2),
                "overhead": round(payload.overhead_cost or 0, 2),
            }
            cost = AvailabilityValue(
                status="AVAILABLE",
                value=round(sum(components.values()), 2),
                unit=payload.currency.upper(),
            )

        return EngineeringRecommendation(
            compatibility=compatibility,
            operation=operation,
            material=selection.material,
            machine=selection.machine,
            tool=selection.tool,
            preliminary_parameters=parameters,
            formulas=formulas,
            units={"length": "mm", "speed": "m/min", "feed": "mm/min", "time": "min"},
            assumptions=[
                "Catalog properties are owner-supplied and versioned.",
                "Straight cutting length is a simplified non-toolpath model.",
            ],
            limitations=[
                "Parameters are not released for production.",
                "Real machine, tool, workholding, stability and coolant require human validation.",
                "No toolpath, G-code, M-code or CNC command is generated.",
            ],
            traceability=selection.traceability,
            data_versions={
                item.kind: item.data_version
                for item in (selection.material, selection.machine, selection.tool)
            },
            rule_version="engineering-rule/v1.0.0",
            source="Vena_IA deterministic preliminary engineering rule",
            source_version="2026.08",
            machining_time_estimate=machining,
            setup_time_estimate=setup,
            total_estimated_time=total,
            cost_estimate=cost,
            cost_components=components,
        )

    def report(self, payload: RecommendationRequest) -> EngineeringReviewReport:
        return self.report_from_recommendation(self.recommend(payload))

    def report_from_recommendation(
        self,
        recommendation: EngineeringRecommendation,
    ) -> EngineeringReviewReport:
        unavailable = [
            name
            for name, value in {
                **recommendation.preliminary_parameters,
                "machining_time": recommendation.machining_time_estimate,
                "setup_time": recommendation.setup_time_estimate,
                "total_time": recommendation.total_estimated_time,
                "cost": recommendation.cost_estimate,
            }.items()
            if value.status == "NOT_AVAILABLE"
        ]
        unavailable.extend(
            [
                "geometry",
                "fixture",
                "coolant",
                "tolerance",
                "surface_finish",
                "toolpath",
                "postprocessor",
            ]
        )
        if recommendation.compatibility.endswith("INCOMPATIBLE"):
            conclusion = "PRELIMINARY_INCOMPATIBLE"
        elif unavailable:
            conclusion = "INSUFFICIENT_DATA"
        else:
            conclusion = "PRELIMINARY_COMPATIBLE"
        completeness = 1 - min(len(unavailable), 10) / 10
        uncertainty = (
            "HIGH_INFORMATION_CONFIDENCE"
            if completeness >= 0.8
            else "MEDIUM_INFORMATION_CONFIDENCE"
            if completeness >= 0.5
            else "LOW_INFORMATION_CONFIDENCE"
        )
        checklist = [
            "material_real_confirmed",
            "material_condition",
            "machine_real_confirmed",
            "machine_capacity",
            "tool_real_confirmed",
            "tool_condition",
            "fixture",
            "rigidity",
            "coolant",
            "accessibility",
            "collision",
            "tolerance",
            "surface_finish",
            "stability",
            "safety",
            "manufacturer_parameters",
            "cam_program",
            "simulation",
            "postprocessor",
            "work_zero",
            "offsets",
            "inspection",
            "final_human_approval",
        ]
        return EngineeringReviewReport(
            recommendation_schema_version=recommendation.schema_version,
            operation=recommendation.operation,
            material=recommendation.material,
            machine=recommendation.machine,
            tool=recommendation.tool,
            compatibility=recommendation.compatibility,
            preliminary_parameters=recommendation.preliminary_parameters,
            formulas=recommendation.formulas,
            units=recommendation.units,
            assumptions=recommendation.assumptions,
            limitations=recommendation.limitations
            + ["This report is not process release and does not authorize a machine."],
            unavailable_items=sorted(set(unavailable)),
            time_estimate=recommendation.total_estimated_time,
            cost_estimate=recommendation.cost_estimate,
            traceability=recommendation.traceability,
            sources=[
                recommendation.source,
                *(
                    item.source
                    for item in (
                        recommendation.material,
                        recommendation.machine,
                        recommendation.tool,
                    )
                ),
            ],
            data_versions=recommendation.data_versions,
            rule_version=recommendation.rule_version,
            uncertainty=uncertainty,
            review_checklist=[
                ReviewChecklistItem(item=item, status="REQUIRED") for item in checklist
            ],
            conclusion=conclusion,
        )
