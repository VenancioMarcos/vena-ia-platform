from __future__ import annotations

import hashlib
import json

from app.modules.cad.features import FeatureRecognitionResult
from app.modules.cad.kernel import KernelGeometry, OpenCascadeGeometryKernel
from app.modules.cad.schemas import (
    BoundingBoxResponse,
    FeatureDimensionResponse,
    GeometryAnalysisContract,
    GeometryFeatureResponse,
    GeometryFeaturesContract,
    GeometryValue,
)
from app.modules.cad.service import CADAnalysisService, CADDocumentAnalysis
from app.modules.cnc.schemas import CNCOperationType, CNCPlanRequest
from app.modules.cnc.service import CNCPlanningService
from app.modules.engineering.planning import FeaturePlanningBridge
from app.modules.engineering.schemas import EngineeringRecommendation, EngineeringReviewReport
from app.modules.engineering.service import EngineeringCatalogService
from app.modules.engineering.workflow_schemas import (
    IntegratedEngineeringReport,
    IntegratedEngineeringWorkflow,
    IntegratedWorkflowRequest,
    SourceDocumentReference,
    WorkflowStatus,
)


WORKFLOW_SCHEMA = "vena-ia.integrated-engineering-workflow/v1"
REPORT_SCHEMA = "vena-ia.integrated-engineering-report/v1"
REVIEW_STATUS = "REQUIRES_HUMAN_REVIEW"


class IntegratedEngineeringWorkflowService:
    """Composes existing deterministic services without creating production authority."""

    def __init__(
        self,
        cad: CADAnalysisService,
        engineering: EngineeringCatalogService,
        cnc: CNCPlanningService,
    ) -> None:
        self._cad = cad
        self._engineering = engineering
        self._cnc = cnc

    def execute(self, payload: IntegratedWorkflowRequest) -> IntegratedEngineeringWorkflow:
        analysis = self._cad.analyze(payload.document_id)
        workflow_id = self._workflow_id(payload)
        geometry = self._geometry_contract(analysis)
        features = self._features_contract(analysis)
        source_reference = f"document:{analysis.document_id}"
        feature_reference = f"feature:{payload.feature_id}"
        planning_reference = f"workflow:{workflow_id}:planning:{payload.feature_id}"
        report_reference = f"workflow:{workflow_id}:report"
        warnings = [
            warning
            for warning in (analysis.geometry_warning, analysis.feature_warning)
            if warning is not None
        ]
        limitations = self._base_limitations(geometry, features)

        if analysis.features is None or analysis.features.status != "AVAILABLE":
            status = WorkflowStatus.BLOCKED_UNSUPPORTED_FEATURE
            missing = ["validated_feature"]
            report = self._report(
                status=status,
                source_reference=source_reference,
                feature_reference=feature_reference,
                planning_reference=None,
                cnc_reference=None,
                engineering_review=None,
                assumptions=[],
                missing=missing,
                limitations=limitations,
            )
            return IntegratedEngineeringWorkflow(
                workflow_id=workflow_id,
                source_document=SourceDocumentReference(
                    document_id=analysis.document_id,
                    filename=analysis.source_filename,
                ),
                geometry=geometry,
                features=features,
                engineering=None,
                planning=None,
                cnc_neutral_plan=None,
                integrated_report=report,
                assumptions=[],
                missing_inputs=missing,
                limitations=limitations,
                warnings=warnings,
                traceability=[source_reference, geometry.schema_version, features.schema_version],
                workflow_status=status,
            )

        planning_result = FeaturePlanningBridge(self._cad, self._engineering).plan_from_analysis(
            payload,
            analysis,
        )
        planning = planning_result.response
        recommendation = planning_result.recommendation
        missing = list(planning.unavailable_inputs)
        if payload.tool_number is None:
            missing.append("tool_number")
        if payload.clearance_z_mm is None:
            missing.append("clearance_z_mm")

        cnc_plan = None
        recommendation_reference = self._recommendation_reference(recommendation)
        if recommendation is not None and not recommendation.compatibility.endswith("INCOMPATIBLE"):
            spindle = recommendation.preliminary_parameters["spindle_speed"]
            feed = recommendation.preliminary_parameters["feed_rate"]
            if spindle.value is None or feed.value is None:
                missing.append("compatible_catalog_parameters")
            elif not missing:
                assert payload.tool_number is not None
                assert payload.clearance_z_mm is not None
                cnc_plan = self._cnc.neutral_plan(
                    CNCPlanRequest(
                        operation=CNCOperationType.DRILLING,
                        tool_number=payload.tool_number,
                        spindle_rpm=spindle.value,
                        feed_mm_min=feed.value,
                        clearance_z_mm=payload.clearance_z_mm,
                    ),
                    planning,
                    planning_reference=planning_reference,
                    recommendation_reference=recommendation_reference,
                )

        if not planning.planning_candidates:
            status = WorkflowStatus.BLOCKED_UNSUPPORTED_FEATURE
        elif missing:
            status = WorkflowStatus.BLOCKED_MISSING_INPUT
        elif recommendation is None or recommendation.compatibility.endswith("INCOMPATIBLE"):
            status = WorkflowStatus.PARTIAL
        elif cnc_plan is None:
            status = WorkflowStatus.PARTIAL
        else:
            status = WorkflowStatus.COMPLETE_PRELIMINARY

        engineering_review = (
            None
            if recommendation is None
            else self._engineering.report_from_recommendation(recommendation)
        )
        assumptions = self._unique(
            [
                *planning.assumptions,
                *([] if recommendation is None else recommendation.assumptions),
                *([] if cnc_plan is None else cnc_plan.machine_neutral_assumptions),
            ]
        )
        report = self._report(
            status=status,
            source_reference=source_reference,
            feature_reference=feature_reference,
            planning_reference=planning_reference,
            cnc_reference=None if cnc_plan is None else f"workflow:{workflow_id}:cnc-neutral-plan",
            engineering_review=engineering_review,
            assumptions=assumptions,
            missing=self._unique(missing),
            limitations=limitations,
        )
        traceability = self._unique(
            [
                source_reference,
                geometry.schema_version,
                features.schema_version,
                feature_reference,
                planning.schema_version,
                planning_reference,
                *planning.traceability,
                *([] if recommendation_reference is None else [recommendation_reference]),
                *([] if cnc_plan is None else [cnc_plan.schema_version, *cnc_plan.traceability]),
                REPORT_SCHEMA,
                report_reference,
            ]
        )
        return IntegratedEngineeringWorkflow(
            workflow_id=workflow_id,
            source_document=SourceDocumentReference(
                document_id=analysis.document_id,
                filename=analysis.source_filename,
            ),
            geometry=geometry,
            features=features,
            engineering=recommendation,
            planning=planning,
            cnc_neutral_plan=cnc_plan,
            integrated_report=report,
            assumptions=assumptions,
            missing_inputs=self._unique(missing),
            limitations=limitations,
            warnings=warnings,
            traceability=traceability,
            workflow_status=status,
        )

    @staticmethod
    def _workflow_id(payload: IntegratedWorkflowRequest) -> str:
        canonical = json.dumps(
            {"schema_version": WORKFLOW_SCHEMA, **payload.model_dump(mode="json")},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"workflow-{hashlib.sha256(canonical).hexdigest()}"

    @staticmethod
    def _recommendation_reference(recommendation: EngineeringRecommendation | None) -> str | None:
        if recommendation is None:
            return None
        versions = ",".join(
            f"{key}={value}" for key, value in sorted(recommendation.data_versions.items())
        )
        return f"engineering-rule:{recommendation.rule_version};catalogs:{versions}"

    @staticmethod
    def _geometry_contract(analysis: CADDocumentAnalysis) -> GeometryAnalysisContract:
        geometry: KernelGeometry | None = analysis.geometry
        return GeometryAnalysisContract(
            status="AVAILABLE" if geometry is not None else "NOT_AVAILABLE",
            unit=analysis.analysis.length_unit,
            bounding_box=None
            if geometry is None
            else BoundingBoxResponse(
                minimum=geometry.bounding_box[0],
                maximum=geometry.bounding_box[1],
                dimensions=(
                    geometry.bounding_box[1][0] - geometry.bounding_box[0][0],
                    geometry.bounding_box[1][1] - geometry.bounding_box[0][1],
                    geometry.bounding_box[1][2] - geometry.bounding_box[0][2],
                ),
            ),
            surface_area=GeometryValue(
                value=None if geometry is None else geometry.surface_area,
                unit=f"{analysis.analysis.length_unit}2",
                status="NOT_AVAILABLE" if geometry is None else "AVAILABLE",
            ),
            volume=GeometryValue(
                value=None if geometry is None else geometry.volume,
                unit=f"{analysis.analysis.length_unit}3",
                status="NOT_AVAILABLE" if geometry is None or geometry.volume is None else "AVAILABLE",
            ),
            topology_valid=None if geometry is None else geometry.topology_valid,
            tolerance=GeometryValue(
                value=None,
                unit=analysis.analysis.length_unit,
                status="NOT_AVAILABLE",
            ),
            entity_count=analysis.analysis.entity_count,
            warnings=[] if analysis.geometry_warning is None else [analysis.geometry_warning],
            uncertainty="VALIDATED_CORPUS_BOUNDARY" if geometry is not None else "UNKNOWN",
            traceability=[
                f"document:{analysis.document_id}",
                f"kernel:{OpenCascadeGeometryKernel.version}",
            ],
            kernel=OpenCascadeGeometryKernel.name,
            kernel_version=OpenCascadeGeometryKernel.version if geometry is not None else None,
            limitations=[
                "No manufacturability or machining-feature claim.",
                "Kernel tolerance is not manufacturing tolerance.",
            ],
        )

    @staticmethod
    def _features_contract(analysis: CADDocumentAnalysis) -> GeometryFeaturesContract:
        result: FeatureRecognitionResult | None = analysis.features
        geometry = analysis.geometry
        return GeometryFeaturesContract(
            status=(
                result.status
                if result is not None
                else ("KERNEL_UNAVAILABLE" if geometry is None else "NOT_RECOGNIZED")
            ),
            kernel=OpenCascadeGeometryKernel.name,
            kernel_version=OpenCascadeGeometryKernel.version if geometry is not None else None,
            shape_class=None if geometry is None else geometry.shape_type,
            feature_rule_version="1.0.0" if result is None else result.rule_version,
            feature_count=0 if result is None else len(result.features),
            features=[]
            if result is None
            else [
                GeometryFeatureResponse(
                    feature_id=f"feature-{index:04d}",
                    feature_type=feature.feature_type,
                    confidence_class=feature.confidence_class,
                    geometry_evidence=list(feature.geometry_evidence),
                    dimensions=[
                        FeatureDimensionResponse(
                            name=dimension.name,
                            value=dimension.value,
                            unit=dimension.unit,
                            source=dimension.source,
                            status=dimension.status,
                        )
                        for dimension in feature.dimensions
                    ],
                    units=sorted({dimension.unit for dimension in feature.dimensions}),
                    topology_refs=list(feature.topology_refs),
                    assumptions=list(feature.assumptions),
                    limitations=list(feature.limitations),
                    review_status=feature.review_status,
                )
                for index, feature in enumerate(result.features, start=1)
            ],
            warnings=(
                [] if analysis.feature_warning is None else [analysis.feature_warning]
            )
            if result is None
            else list(result.warnings),
            limitations=["Feature recognition requires available, valid kernel topology."]
            if result is None
            else list(result.limitations),
            traceability=[
                f"document:{analysis.document_id}",
                f"kernel:{OpenCascadeGeometryKernel.version}",
                f"feature-rule:{'1.0.0' if result is None else result.rule_version}",
            ],
            uncertainty="UNKNOWN" if result is None else result.uncertainty,
            tolerance=GeometryValue(
                value=None if result is None else result.tolerance,
                unit=analysis.analysis.length_unit,
                status="NOT_AVAILABLE" if result is None else "AVAILABLE",
            ),
        )

    @staticmethod
    def _base_limitations(
        geometry: GeometryAnalysisContract,
        features: GeometryFeaturesContract,
    ) -> list[str]:
        return IntegratedEngineeringWorkflowService._unique(
            [
                *geometry.limitations,
                *features.limitations,
                "NON_PRODUCTION: the workflow is preliminary evidence only.",
                "No toolpath, coordinates, cutter-location data or postprocessor output.",
                "No G-code, M-code, NC/DNC, transmission or machine control.",
                "Catalogs remain global authenticated resources in Package 1.",
                "Qualified human review is mandatory for every downstream use.",
            ]
        )

    @staticmethod
    def _report(
        *,
        status: WorkflowStatus,
        source_reference: str,
        feature_reference: str,
        planning_reference: str | None,
        cnc_reference: str | None,
        engineering_review: EngineeringReviewReport | None,
        assumptions: list[str],
        missing: list[str],
        limitations: list[str],
    ) -> IntegratedEngineeringReport:
        return IntegratedEngineeringReport(
            source_document_reference=source_reference,
            geometry_reference="vena-ia.geometry-analysis/v1",
            feature_reference=feature_reference,
            planning_reference=planning_reference,
            cnc_neutral_plan_reference=cnc_reference,
            engineering_review=engineering_review,
            assumptions=assumptions,
            missing_inputs=IntegratedEngineeringWorkflowService._unique(missing),
            limitations=limitations,
            human_review_checklist=[
                "Confirm source geometry and feature evidence.",
                "Confirm material, machine, tool and catalog versions.",
                "Confirm tolerance, fixture, coolant and material condition.",
                "Reject any interpretation as production or machine approval.",
            ],
            conclusion=status,
        )

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
