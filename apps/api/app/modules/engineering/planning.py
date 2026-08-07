from __future__ import annotations

import math
from dataclasses import dataclass

from fastapi import HTTPException

from app.modules.cad.features import GeometryFeature, REVIEW_STATUS as FEATURE_REVIEW_STATUS
from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.service import CADAnalysisService, CADDocumentAnalysis
from app.modules.engineering.schemas import (
    EngineeringRecommendation,
    EngineeringRecommendationReference,
    FeaturePlanningCandidate,
    FeaturePlanningDimension,
    FeaturePlanningRequest,
    FeaturePlanningResponse,
    RecommendationRequest,
    REVIEW_STATUS,
)
from app.modules.engineering.service import EngineeringCatalogService


FEATURE_PLANNING_RULE_VERSION = "1.0.0"
MAX_FEATURES_PER_REQUEST = 100
FEATURE_SCHEMA_VERSION = "vena-ia.geometry-features/v1"
ENGINEERING_SCHEMA_VERSION = "vena-ia.engineering-recommendation/v1"


@dataclass(frozen=True)
class FeaturePlanningResult:
    response: FeaturePlanningResponse
    recommendation: EngineeringRecommendation | None


class FeaturePlanningBridge:
    def __init__(
        self,
        cad: CADAnalysisService,
        engineering: EngineeringCatalogService,
    ) -> None:
        self._cad = cad
        self._engineering = engineering

    def plan(self, payload: FeaturePlanningRequest) -> FeaturePlanningResponse:
        analysis = self._cad.analyze(payload.document_id)
        return self.plan_from_analysis(payload, analysis).response

    def plan_from_analysis(
        self,
        payload: FeaturePlanningRequest,
        analysis: CADDocumentAnalysis,
    ) -> FeaturePlanningResult:
        result = analysis.features
        if result is None or result.status != "AVAILABLE":
            raise HTTPException(status_code=422, detail="Validated feature analysis unavailable")
        if len(result.features) > MAX_FEATURES_PER_REQUEST:
            raise HTTPException(status_code=422, detail="Feature planning resource limit exceeded")
        try:
            feature_index = int(payload.feature_id.removeprefix("feature-"))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Feature not found") from exc
        if feature_index < 1 or feature_index > len(result.features):
            raise HTTPException(status_code=404, detail="Feature not found")
        feature = result.features[feature_index - 1]
        if feature.review_status != FEATURE_REVIEW_STATUS:
            raise HTTPException(status_code=422, detail="Feature review evidence is invalid")
        dimensions = self._validated_dimensions(feature)
        candidates = self._candidates(feature)
        required_inputs = {
            "material": payload.material_id,
            "machine": payload.machine_id,
            "tool": payload.tool_id,
            "manufacturing_intent": payload.manufacturing_intent,
            "drawing_tolerance": payload.drawing_tolerance,
            "surface_finish": payload.surface_finish,
            "fixture": payload.fixture,
            "coolant": payload.coolant,
            "material_condition": payload.material_condition,
        }
        unavailable = [name for name, value in required_inputs.items() if value is None]
        recommendation = self._recommend(payload, feature, candidates)
        recommendation_reference = (
            None
            if recommendation is None
            else EngineeringRecommendationReference(
                schema_version=recommendation.schema_version,
                status=recommendation.status,
                compatibility=recommendation.compatibility,
                operation=recommendation.operation,
                preliminary_parameters=recommendation.preliminary_parameters,
                limitations=recommendation.limitations,
                traceability=recommendation.traceability,
                data_versions=recommendation.data_versions,
                rule_version=recommendation.rule_version,
            )
        )
        completeness = (
            "PARTIAL_CONTEXT"
            if candidates
            else "INSUFFICIENT_CONTEXT"
        )
        if not candidates:
            status = "NO_PLANNING_CANDIDATE"
        elif recommendation is None:
            status = "REQUIRED_INPUT"
        else:
            status = "PRELIMINARY_PLANNING_AVAILABLE"
        traceability = [
            f"document:{analysis.document_id}",
            f"kernel:{OpenCascadeGeometryKernel.version}",
            f"feature-rule:{result.rule_version}",
            f"feature:{payload.feature_id}",
            f"planning-rule:{FEATURE_PLANNING_RULE_VERSION}",
        ]
        if recommendation is not None:
            traceability.extend(
                [
                    f"engineering-rule:{recommendation.rule_version}",
                    *recommendation.traceability,
                ]
            )
        response = FeaturePlanningResponse(
            status=status,
            feature_id=payload.feature_id,
            feature_type=feature.feature_type,
            feature_dimensions=dimensions,
            planning_rule_version=FEATURE_PLANNING_RULE_VERSION,
            planning_candidates=candidates,
            required_inputs=list(required_inputs),
            unavailable_inputs=unavailable,
            engineering_recommendation=recommendation_reference,
            planning_context_completeness=completeness,
            geometric_evidence_confidence=feature.confidence_class,
            assumptions=[
                "A planning candidate is a non-executable possibility, not a selected process.",
                "Geometry evidence does not establish manufacturing intent.",
            ],
            limitations=[
                "No manufacturability or production-safety claim.",
                "No CAM, toolpath, coordinates, G-code, M-code or CNC command.",
                "Machine, tool, fixture and process require qualified human validation.",
            ],
            traceability=traceability,
            uncertainty=(
                "Geometric evidence confidence and planning context completeness are independent."
            ),
            review_status=REVIEW_STATUS,
        )
        return FeaturePlanningResult(response=response, recommendation=recommendation)

    @staticmethod
    def _validated_dimensions(feature: GeometryFeature) -> list[FeaturePlanningDimension]:
        dimensions: list[FeaturePlanningDimension] = []
        for dimension in feature.dimensions:
            if dimension.status == "AVAILABLE" and (
                dimension.value is None
                or not math.isfinite(dimension.value)
                or dimension.value <= 0
                or not dimension.unit
            ):
                raise HTTPException(status_code=422, detail="Feature dimension evidence is invalid")
            dimensions.append(
                FeaturePlanningDimension(
                    name=dimension.name,
                    value=dimension.value,
                    unit=dimension.unit,
                    source=dimension.source,
                    status=dimension.status,
                )
            )
        return dimensions

    @staticmethod
    def _candidates(feature: GeometryFeature) -> list[FeaturePlanningCandidate]:
        if feature.feature_type != "THROUGH_CYLINDRICAL_HOLE":
            return []
        return [
            FeaturePlanningCandidate(
                candidate_type="DRILLING_CANDIDATE",
                operation="drilling",
                status="POSSIBLE_NOT_SELECTED",
                evidence=[
                    "Validated feature type is THROUGH_CYLINDRICAL_HOLE.",
                    *feature.geometry_evidence,
                ],
                executable_output=False,
            )
        ]

    def _recommend(
        self,
        payload: FeaturePlanningRequest,
        feature: GeometryFeature,
        candidates: list[FeaturePlanningCandidate],
    ) -> EngineeringRecommendation | None:
        if not candidates or not all((payload.material_id, payload.machine_id, payload.tool_id)):
            return None
        assert payload.material_id is not None
        assert payload.machine_id is not None
        assert payload.tool_id is not None
        depth = next(
            (
                dimension.value
                for dimension in feature.dimensions
                if dimension.name == "depth" and dimension.status == "AVAILABLE"
            ),
            None,
        )
        return self._engineering.recommend(
            RecommendationRequest(
                material_id=payload.material_id,
                machine_id=payload.machine_id,
                tool_id=payload.tool_id,
                operation="drilling",
                cutting_length_mm=depth,
                setup_time_min=payload.setup_time_min,
                machine_hour_rate=payload.machine_hour_rate,
                tool_cost_allocation=payload.tool_cost_allocation,
                consumable_cost=payload.consumable_cost,
                overhead_cost=payload.overhead_cost,
                currency=payload.currency,
            )
        )
