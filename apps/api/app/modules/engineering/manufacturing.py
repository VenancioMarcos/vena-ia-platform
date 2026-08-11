from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict

from app.modules.cad.evidence import GeometryTopologyEvidence, TopologyElementEvidence
from app.modules.cad.service import CADAnalysisService
from app.modules.engineering.manufacturing_schemas import (
    AccessibilityCandidate,
    DatumCandidate,
    FinalGeometryReference,
    ManufacturingGeometryModel,
    ManufacturingPlanningRequest,
    ManufacturingRegion,
    MissingManufacturingInput,
    PlanningVerificationEvidence,
    ProcessOperationCandidate,
    SetupCandidate,
    StockEvidence,
    WCSCandidate,
)
from app.modules.engineering.schemas import (
    EngineeringRecommendation,
    EngineeringRecommendationReference,
    RecommendationRequest,
)
from app.modules.engineering.service import EngineeringCatalogService


MANUFACTURING_RULE_VERSION = "1.0.0"
MAX_CANDIDATES = 256


class ManufacturingPlanningError(Exception):
    pass


def _hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _volume(bounds: tuple[tuple[float, float, float], tuple[float, float, float]]) -> float:
    minimum, maximum = bounds
    return math.prod(maximum[index] - minimum[index] for index in range(3))


def _contains(
    outer: tuple[tuple[float, float, float], tuple[float, float, float]],
    inner: tuple[tuple[float, float, float], tuple[float, float, float]],
) -> bool:
    return all(
        outer[0][index] <= inner[0][index] and outer[1][index] >= inner[1][index]
        for index in range(3)
    )


class ManufacturingPlanningService:
    """Deterministic manufacturing interpretation without toolpath authority."""

    def __init__(self, cad: CADAnalysisService, engineering: EngineeringCatalogService) -> None:
        self._cad = cad
        self._engineering = engineering

    def plan(self, payload: ManufacturingPlanningRequest) -> ManufacturingGeometryModel:
        analysis = self._cad.analyze(payload.document_id)
        evidence = analysis.topology_evidence
        geometry = analysis.geometry
        if evidence is None or geometry is None:
            raise ManufacturingPlanningError("General geometry evidence is unavailable")

        evidence_hash = _hash(asdict(evidence))
        final_bounds = geometry.bounding_box
        final_reference = FinalGeometryReference(
            source_geometry_hash=evidence.source_sha256,
            topology_evidence_schema=evidence.schema_version,
            topology_evidence_hash=evidence_hash,
            normalized_unit=evidence.normalized_unit or "UNKNOWN",
            bounds=final_bounds,
            topology_valid=evidence.topology_valid,
        )
        missing: list[MissingManufacturingInput] = []
        ambiguities: list[str] = []
        unknown_regions: list[ManufacturingRegion] = []

        evidence_ready = evidence.status in {"AVAILABLE", "AVAILABLE_WITH_AMBIGUITY"}
        if not evidence_ready:
            missing.append(
                self._missing(
                    "geometry_evidence",
                    f"Topology evidence status is {evidence.status}.",
                    "GEOMETRY_EVIDENCE_GATE",
                    "vena-ia.geometry-topology-evidence/v1",
                    [*evidence.warnings, *evidence.unsupported],
                )
            )
        if evidence.normalized_unit != "mm":
            missing.append(
                self._missing(
                    "normalized_unit",
                    "Manufacturing interpretation requires unambiguous normalized units.",
                    "UNIT_GATE",
                    "mm",
                    [f"normalized_unit:{evidence.normalized_unit}"],
                )
            )

        stock = self._stock(payload, final_bounds, geometry.volume, missing)
        protected = self._protected_regions(evidence)
        accessibility = self._accessibility(evidence, ambiguities)
        datums, wcs, setups = self._setup_candidates(
            evidence,
            accessibility,
            payload.fixture,
        )
        if not accessibility:
            missing.append(
                self._missing(
                    "setup_orientation",
                    "No cardinal planar approach direction is proven.",
                    "3_AXIS_ACCESSIBILITY_GATE",
                    "unit direction vector",
                    ["cardinal-planar-surface"],
                )
            )
        if payload.fixture is None:
            missing.append(
                self._missing(
                    "fixture",
                    "Fixture/keep-out evidence is required to verify a setup.",
                    "SETUP_VERIFICATION_GATE",
                    "text fixture constraints",
                    ["fixture", "keep-outs", "clamping constraints"],
                )
            )
        if payload.datum_wcs_input is None:
            missing.append(
                self._missing(
                    "datum_wcs_input",
                    "Geometric datum/WCS candidates require confirmation.",
                    "DATUM_WCS_GATE",
                    "datum/WCS confirmation",
                    [candidate.candidate_id for candidate in datums],
                )
            )
        if payload.manufacturing_intent is None:
            missing.append(
                self._missing(
                    "manufacturing_intent",
                    "Geometry does not establish a manufacturing operation.",
                    "INTENT_GATE",
                    "milling|drilling",
                    ["authorized user/configuration intent"],
                )
            )

        recommendation = self._recommendation(payload, missing)
        removal, inaccessible, stock_unknown = self._removal_regions(
            stock, final_reference, geometry.volume
        )
        unknown_regions.extend(stock_unknown)
        operations = self._operations(
            payload,
            removal,
            setups,
            evidence,
            recommendation,
            missing,
        )
        precedence = self._precedence(operations)

        if stock.status == "INVALID" or not evidence.topology_valid:
            status = "INVALID"
        elif missing:
            status = "REQUIRES_INPUT"
        elif recommendation is not None and recommendation.compatibility.endswith("INCOMPATIBLE"):
            status = "BLOCKED_RESOURCE_MISMATCH"
        elif operations:
            status = "READY_FOR_REVIEW"
        else:
            status = "NOT_PLANNED"

        seed = {
            "rule": MANUFACTURING_RULE_VERSION,
            "request": payload.model_dump(mode="json"),
            "evidence_hash": evidence_hash,
            "stock": stock.model_dump(mode="json"),
            "operations": [item.model_dump(mode="json") for item in operations],
            "precedence": precedence,
        }
        replay_hash = _hash(seed)
        resource_status = (
            "NOT_SELECTED"
            if recommendation is None
            else recommendation.compatibility
        )
        verification = PlanningVerificationEvidence(
            status="PASS_REQUIRES_HUMAN_REVIEW" if status == "READY_FOR_REVIEW" else "BLOCKED",
            coherent=status not in {"INVALID", "BLOCKED_RESOURCE_MISMATCH"},
            logical_coverage="COMPLETE" if operations and not missing else "INCOMPLETE",
            missing_input_count=len(missing),
            resource_compatibility=resource_status,
            precedence_valid=self._precedence_valid(operations),
            setup_feasibility="CANDIDATE_ONLY" if setups else "NOT_AVAILABLE",
            deterministic_replay_hash=replay_hash,
            checks=[
                "geometry-evidence-version-and-hash",
                "stock-contains-final-geometry",
                "organization-scoped-resource-authorization",
                "operation-intent-is-explicit",
                "precedence-dependencies-reference-known-candidates",
                "no-executable-output",
            ],
            limitations=[
                "Planning verification is not material-removal simulation.",
                "No cutter sweep, collision or machine kinematics is evaluated.",
                "Physical validation and production authority remain false.",
            ],
        )
        return ManufacturingGeometryModel(
            status=status,
            final_geometry=final_reference,
            stock=stock,
            removal_regions=removal,
            protected_regions=protected,
            inaccessible_regions=inaccessible,
            unknown_regions=unknown_regions,
            accessibility_candidates=accessibility,
            datum_candidates=datums,
            wcs_candidates=wcs,
            setup_candidates=setups,
            operation_candidates=operations,
            precedence_rules=precedence,
            missing_inputs=missing,
            ambiguities=ambiguities,
            geometric_constraints=[
                "3_AXIS_2_5D_ORIENTED_PLANNING_ONLY",
                "STOCK_MUST_CONTAIN_FINAL_GEOMETRY",
                "CARDINAL_APPROACH_DIRECTIONS_ONLY",
            ],
            assumptions=[
                "OCCT transferred coordinates are normalized to millimetres.",
                "Final B-Rep surfaces are protected by default.",
            ],
            confidence_evidence=[
                f"geometry-evidence:{evidence_hash}",
                f"manufacturing-rule:{MANUFACTURING_RULE_VERSION}",
            ],
            provenance=[
                *evidence.provenance,
                *([] if payload.stock is None else [f"stock:{payload.stock.source_ref}"]),
            ],
            limitations=[
                "Manufacturing intent is never inferred from a surface class.",
                "Accessibility is preliminary and excludes holder/tool collision.",
                "No toolpath, cutter location, postprocessor, G-code or machine output.",
            ],
            recommendation=self._recommendation_reference(recommendation),
            verification=verification,
        )

    @staticmethod
    def _missing(
        field: str,
        reason: str,
        gate: str,
        expected: str,
        evidence: list[str],
    ) -> MissingManufacturingInput:
        return MissingManufacturingInput(
            field=field,
            reason=reason,
            blocking_gate=gate,
            expected_type_unit=expected,
            evidence_missing=evidence,
        )

    def _stock(
        self,
        payload: ManufacturingPlanningRequest,
        final_bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
        final_volume: float | None,
        missing: list[MissingManufacturingInput],
    ) -> StockEvidence:
        stock = payload.stock
        if stock is None or stock.status == "MISSING":
            missing.append(
                self._missing(
                    "stock",
                    "Stock cannot be inferred from the final-part bounding box.",
                    "STOCK_GATE",
                    "bounded solid in mm with provenance",
                    ["stock bounds", "stock source"],
                )
            )
            return StockEvidence(
                status="MISSING",
                minimum=None,
                maximum=None,
                unit=None,
                source_ref=None,
                contains_final_geometry=None,
                volume=None,
                limitations=["Final-part bounding box is not accepted as stock fact."],
            )
        if stock.status in {"AMBIGUOUS", "INVALID"} or stock.minimum is None or stock.maximum is None:
            missing.append(
                self._missing(
                    "stock",
                    f"Stock status is {stock.status}.",
                    "STOCK_GATE",
                    "valid bounded solid in mm",
                    ["unambiguous stock bounds"],
                )
            )
            return StockEvidence(
                status=stock.status,
                minimum=stock.minimum,
                maximum=stock.maximum,
                unit=stock.unit,
                source_ref=stock.source_ref,
                contains_final_geometry=None,
                volume=None,
                limitations=["Removal evidence withheld for invalid/ambiguous stock."],
            )
        bounds = (stock.minimum, stock.maximum)
        finite = all(math.isfinite(value) for point in bounds for value in point)
        ordered = all(stock.maximum[index] > stock.minimum[index] for index in range(3))
        contains_final = finite and ordered and _contains(bounds, final_bounds)
        stock_volume = _volume(bounds) if finite and ordered else None
        valid = bool(
            contains_final
            and stock_volume is not None
            and (final_volume is None or stock_volume >= final_volume)
        )
        if not valid:
            missing.append(
                self._missing(
                    "stock",
                    "Stock is invalid or does not contain final geometry.",
                    "STOCK_CONTAINMENT_GATE",
                    "containing bounded solid in mm",
                    ["stock >= final B-Rep"],
                )
            )
        return StockEvidence(
            status=stock.status if valid else "INVALID",
            minimum=stock.minimum,
            maximum=stock.maximum,
            unit=stock.unit,
            source_ref=stock.source_ref,
            contains_final_geometry=contains_final,
            volume=stock_volume,
            limitations=["Stock is an explicit/configured fact, not an inferred final-part box."],
        )

    @staticmethod
    def _protected_regions(evidence: GeometryTopologyEvidence) -> list[ManufacturingRegion]:
        return [
            ManufacturingRegion(
                region_id=f"protected-{element.element_id}",
                region_type="FINAL_SURFACE_PROTECTED",
                status="AVAILABLE",
                bounds=element.bounds,
                volume=None,
                topology_refs=[element.element_id],
                evidence=["Final B-Rep face is protected by default."],
                limitations=["Protection does not define finish, tolerance or operation."],
            )
            for element in evidence.elements
            if element.kind == "FACE"
        ][:MAX_CANDIDATES]

    @staticmethod
    def _normal(element: TopologyElementEvidence) -> tuple[float, float, float] | None:
        keys = ("normal_x", "normal_y", "normal_z")
        if not all(key in element.metrics for key in keys):
            return None
        normal = tuple(float(element.metrics[key]) for key in keys)
        if not math.isclose(sum(value * value for value in normal), 1.0, abs_tol=1e-6):
            return None
        cardinal = sum(math.isclose(abs(value), 1.0, abs_tol=1e-6) for value in normal) == 1
        zeros = sum(math.isclose(value, 0.0, abs_tol=1e-6) for value in normal) == 2
        return normal if cardinal and zeros else None  # type: ignore[return-value]

    def _accessibility(
        self,
        evidence: GeometryTopologyEvidence,
        ambiguities: list[str],
    ) -> list[AccessibilityCandidate]:
        grouped: dict[tuple[float, float, float], list[str]] = {}
        for element in evidence.elements:
            if element.kind != "FACE" or element.geometry_type != "PLANE":
                continue
            normal = self._normal(element)
            if normal is None:
                ambiguities.append(f"non-cardinal-or-unknown-normal:{element.element_id}")
                continue
            grouped.setdefault(normal, []).append(element.element_id)
        return [
            AccessibilityCandidate(
                candidate_id=f"access-{_hash(direction)[:16]}",
                approach_direction=direction,
                accessible_surface_refs=sorted(refs),
                blocked_surface_refs=[],
                status="CANDIDATE_REQUIRES_FIXTURE_AND_COLLISION_REVIEW",
                evidence=["Cardinal outward planar normal from topology evidence."],
                limitations=["No dynamic tool/holder collision or kinematics evaluated."],
            )
            for direction, refs in sorted(grouped.items())
        ][:MAX_CANDIDATES]

    def _setup_candidates(
        self,
        evidence: GeometryTopologyEvidence,
        accessibility: list[AccessibilityCandidate],
        fixture: str | None,
    ) -> tuple[list[DatumCandidate], list[WCSCandidate], list[SetupCandidate]]:
        faces = sorted(
            (
                element
                for element in evidence.elements
                if element.kind == "FACE" and self._normal(element) is not None
            ),
            key=lambda element: (-element.metrics.get("area", 0.0), element.element_id),
        )[:MAX_CANDIDATES]
        datums = [
            DatumCandidate(
                candidate_id=f"datum-{element.element_id}",
                surface_ref=element.element_id,
                origin_candidate=(
                    element.metrics.get("location_x", 0.0),
                    element.metrics.get("location_y", 0.0),
                    element.metrics.get("location_z", 0.0),
                ),
                normal=self._normal(element) or (0.0, 0.0, 0.0),
                area=element.metrics.get("area", 0.0),
            )
            for element in faces
        ]
        wcs = [
            WCSCandidate(
                candidate_id=f"wcs-{datum.surface_ref}",
                datum_candidate_id=datum.candidate_id,
                origin=datum.origin_candidate,
                z_direction=datum.normal,
            )
            for datum in datums
        ]
        setups = [
            SetupCandidate(
                candidate_id=f"setup-{candidate.candidate_id}",
                orientation=candidate.approach_direction,
                accessibility_candidate_id=candidate.candidate_id,
                fixture_status="PROVIDED_REQUIRES_REVIEW" if fixture else "MISSING",
                status="REQUIRES_REVIEW" if fixture else "REQUIRES_INPUT",
                evidence=[*candidate.evidence, *([] if fixture is None else [f"fixture:{fixture}"])],
                limitations=["Candidate is not a production setup or machine offset."],
            )
            for candidate in accessibility
        ]
        return datums, wcs, setups

    @staticmethod
    def _removal_regions(
        stock: StockEvidence,
        final: FinalGeometryReference,
        final_volume: float | None,
    ) -> tuple[
        list[ManufacturingRegion],
        list[ManufacturingRegion],
        list[ManufacturingRegion],
    ]:
        if stock.status not in {"PROVIDED", "DERIVED_FROM_AUTHORIZED_CONFIGURATION"}:
            return [], [], []
        if not stock.contains_final_geometry or stock.minimum is None or stock.maximum is None:
            return [], [
                ManufacturingRegion(
                    region_id="inaccessible-invalid-stock",
                    region_type="INCONSISTENT_STOCK_FINAL_RELATION",
                    status="INVALID",
                    bounds=None,
                    volume=None,
                    topology_refs=[],
                    evidence=["Stock containment gate failed."],
                    limitations=["No operation may be generated."],
                )
            ], []
        sx0, sy0, sz0 = stock.minimum
        sx1, sy1, sz1 = stock.maximum
        (fx0, fy0, fz0), (fx1, fy1, fz1) = final.bounds
        slab_bounds = [
            ((sx0, sy0, sz0), (fx0, sy1, sz1)),
            ((fx1, sy0, sz0), (sx1, sy1, sz1)),
            ((fx0, sy0, sz0), (fx1, fy0, sz1)),
            ((fx0, fy1, sz0), (fx1, sy1, sz1)),
            ((fx0, fy0, sz0), (fx1, fy1, fz0)),
            ((fx0, fy0, fz1), (fx1, fy1, sz1)),
        ]
        removal: list[ManufacturingRegion] = []
        for index, bounds in enumerate(slab_bounds, start=1):
            if not all(bounds[1][axis] > bounds[0][axis] for axis in range(3)):
                continue
            removal.append(
                ManufacturingRegion(
                    region_id=f"removal-{_hash([bounds, final.source_geometry_hash])[:16]}",
                    region_type="OUTSIDE_FINAL_ENVELOPE_REMOVAL_CANDIDATE",
                    status="AVAILABLE",
                    bounds=bounds,
                    volume=_volume(bounds),
                    topology_refs=[],
                    evidence=[
                        "Explicit/configured stock contains final geometry.",
                        f"final-geometry:{final.topology_evidence_hash}",
                        f"non-overlapping-envelope-slab:{index}",
                    ],
                    limitations=[
                        "Subregion covers stock outside the final envelope only.",
                        "It is geometric evidence, not an operation or toolpath.",
                    ],
                )
            )
        final_envelope_volume = _volume(final.bounds)
        unknown_volume = (
            None if final_volume is None else max(final_envelope_volume - final_volume, 0.0)
        )
        unknown = []
        if unknown_volume is None or unknown_volume > 1e-9:
            unknown.append(
                ManufacturingRegion(
                    region_id=f"unknown-{_hash([final.bounds, final.source_geometry_hash])[:16]}",
                    region_type="UNKNOWN_WITHIN_FINAL_ENVELOPE",
                    status="UNKNOWN",
                    bounds=final.bounds,
                    volume=unknown_volume,
                    topology_refs=[],
                    evidence=["Envelope is not treated as exact final-part geometry."],
                    limitations=[
                        "Boolean B-Rep decomposition inside the envelope is not claimed."
                    ],
                )
            )
        return removal, [], unknown

    def _recommendation(
        self,
        payload: ManufacturingPlanningRequest,
        missing: list[MissingManufacturingInput],
    ) -> EngineeringRecommendation | None:
        resources = {
            "material_id": payload.material_id,
            "machine_id": payload.machine_id,
            "tool_id": payload.tool_id,
        }
        absent = [field for field, value in resources.items() if value is None]
        if absent or payload.manufacturing_intent is None:
            for field in absent:
                missing.append(
                    self._missing(
                        field,
                        "Authorized organization-scoped resource is required.",
                        "RESOURCE_GATE",
                        "catalog resource id",
                        [field, "active organization membership"],
                    )
                )
            return None
        assert payload.material_id and payload.machine_id and payload.tool_id
        return self._engineering.recommend(
            RecommendationRequest(
                material_id=payload.material_id,
                machine_id=payload.machine_id,
                tool_id=payload.tool_id,
                operation=payload.manufacturing_intent,
            )
        )

    def _operations(
        self,
        payload: ManufacturingPlanningRequest,
        removal: list[ManufacturingRegion],
        setups: list[SetupCandidate],
        evidence: GeometryTopologyEvidence,
        recommendation: EngineeringRecommendation | None,
        missing: list[MissingManufacturingInput],
    ) -> list[ProcessOperationCandidate]:
        if not removal or payload.manufacturing_intent is None or recommendation is None:
            return []
        if recommendation.compatibility.endswith("INCOMPATIBLE") or not setups:
            return []
        if payload.manufacturing_intent == "drilling":
            missing.append(
                self._missing(
                    "drilling_target_confirmation",
                    "Cylindrical geometry alone does not prove a drilling target.",
                    "NO_FALSE_MANUFACTURING_CLAIM_GATE",
                    "confirmed target feature/region",
                    ["manufacturing feature evidence beyond surface classification"],
                )
            )
            return []
        setup = setups[0]
        parameters: dict[str, object] = {
            key: value.model_dump(mode="json")
            for key, value in recommendation.preliminary_parameters.items()
        }
        rough_id = f"operation-{_hash([removal[0].region_id, 'rough', setup.candidate_id])[:16]}"
        operations = [
            ProcessOperationCandidate(
                candidate_id=rough_id,
                operation_class="GEOMETRIC_ROUGHING_CANDIDATE",
                requested_intent=payload.manufacturing_intent,
                setup_candidate_id=setup.candidate_id,
                target_region_refs=[region.region_id for region in removal],
                resource_requirements=[
                    payload.material_id or "",
                    payload.machine_id or "",
                    payload.tool_id or "",
                ],
                parameters=parameters,
                missing_parameters=[
                    key
                    for key, value in parameters.items()
                    if isinstance(value, dict) and value.get("status") != "AVAILABLE"
                ],
                dependencies=[],
                status="CANDIDATE_REQUIRES_HUMAN_REVIEW",
                evidence=[
                    f"explicit-intent:{payload.manufacturing_intent}",
                    f"manufacturing-rule:{MANUFACTURING_RULE_VERSION}",
                    *[region.region_id for region in removal],
                ],
            )
        ]
        if payload.surface_finish or payload.drawing_tolerance:
            operations.append(
                ProcessOperationCandidate(
                    candidate_id=f"operation-{_hash([rough_id, 'finish'])[:16]}",
                    operation_class="FINISHING_REVIEW_CANDIDATE",
                    requested_intent=payload.manufacturing_intent,
                    setup_candidate_id=setup.candidate_id,
                    target_region_refs=[region.region_id for region in removal],
                    resource_requirements=[payload.machine_id or "", payload.tool_id or ""],
                    parameters={
                        "drawing_tolerance": payload.drawing_tolerance,
                        "surface_finish": payload.surface_finish,
                    },
                    missing_parameters=[],
                    dependencies=[rough_id],
                    status="CANDIDATE_REQUIRES_HUMAN_REVIEW",
                    evidence=["Explicit finishing/tolerance input; roughing precedes finishing."],
                )
            )
        return operations

    @staticmethod
    def _precedence(operations: list[ProcessOperationCandidate]) -> list[str]:
        return [
            f"{dependency} -> {operation.candidate_id}"
            for operation in operations
            for dependency in operation.dependencies
        ]

    @staticmethod
    def _precedence_valid(operations: list[ProcessOperationCandidate]) -> bool:
        known = {operation.candidate_id for operation in operations}
        return all(
            dependency in known
            for operation in operations
            for dependency in operation.dependencies
        )

    @staticmethod
    def _recommendation_reference(
        recommendation: EngineeringRecommendation | None,
    ) -> EngineeringRecommendationReference | None:
        if recommendation is None:
            return None
        return EngineeringRecommendationReference(
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
