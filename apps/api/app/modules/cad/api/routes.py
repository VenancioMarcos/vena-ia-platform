from fastapi import APIRouter, HTTPException

from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.cad.dependencies import CADAnalysisServiceDependency
from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.parser import StepParseError
from app.modules.cad.schemas import (
    BoundingBoxResponse,
    CADAnalysisResponse,
    GeometryKernelDecision,
    GeometryAnalysisContract,
    GeometryFeatureResponse,
    GeometryFeaturesContract,
    GeometryTopologyEvidenceContract,
    TopologyElementEvidenceResponse,
    TopologyTransformEvidence,
    FeatureDimensionResponse,
    GeometryValue,
)
from app.modules.cad.service import CADContentUnavailableError
from app.modules.documents.service import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    InvalidDocumentError,
    ProjectNotFoundError,
)

router = APIRouter(prefix="/cad", tags=["cad"])


@router.get("/kernel-decision", response_model=GeometryKernelDecision)
def geometry_kernel_decision(
    _current_user: CurrentUserDependency,
) -> GeometryKernelDecision:
    return GeometryKernelDecision(
        decision="B_APPROVED_WITH_RESTRICTIONS",
        candidate="OpenCascade Technology",
        license="LGPL-2.1-with-exception",
        integration_status="CONTROLLED_INTEGRATION_ACTIVE",
        official_python="3.13.11",
        experimental_python="3.14.6",
        contract_schema="vena-ia.geometry-analysis/v1",
        limitations=[
            "Binary/package compatibility must pass Windows, Linux and Docker gates.",
            "Feature recognition is limited to validated synthetic corpus rules.",
            "Analysis never establishes manufacturability or machine safety.",
        ],
    )


@router.post(
    "/documents/{document_id}/analysis",
    response_model=CADAnalysisResponse,
)
def analyze_step_document(
    document_id: str,
    service: CADAnalysisServiceDependency,
) -> CADAnalysisResponse:
    try:
        result = service.analyze(document_id)
    except (DocumentNotFoundError, ProjectNotFoundError, DocumentAccessDeniedError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StepParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CADContentUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    analysis = result.analysis
    bounding_box = (
        None
        if analysis.bounding_box is None
        else BoundingBoxResponse(
            minimum=analysis.bounding_box.minimum,
            maximum=analysis.bounding_box.maximum,
            dimensions=analysis.bounding_box.dimensions,
        )
    )
    geometry = result.geometry
    geometry_contract = GeometryAnalysisContract(
        status="AVAILABLE" if geometry is not None else "NOT_AVAILABLE",
        unit=analysis.length_unit,
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
            unit=f"{analysis.length_unit}2",
            status="NOT_AVAILABLE" if geometry is None else "AVAILABLE",
        ),
        volume=GeometryValue(
            value=None if geometry is None else geometry.volume,
            unit=f"{analysis.length_unit}3",
            status="NOT_AVAILABLE" if geometry is None or geometry.volume is None else "AVAILABLE",
        ),
        topology_valid=None if geometry is None else geometry.topology_valid,
        tolerance=GeometryValue(value=None, unit=analysis.length_unit, status="NOT_AVAILABLE"),
        entity_count=analysis.entity_count,
        warnings=[] if result.geometry_warning is None else [result.geometry_warning],
        uncertainty="VALIDATED_CORPUS_BOUNDARY" if geometry is not None else "UNKNOWN",
        traceability=[
            f"document:{result.document_id}",
            f"kernel:{OpenCascadeGeometryKernel.version}",
        ],
        kernel=OpenCascadeGeometryKernel.name,
        kernel_version=OpenCascadeGeometryKernel.version if geometry is not None else None,
        limitations=[
            "No manufacturability or machining-feature claim.",
            "Kernel tolerance is not manufacturing tolerance.",
        ],
    )
    feature_result = result.features
    feature_contract = GeometryFeaturesContract(
        status=(
            feature_result.status
            if feature_result is not None
            else ("KERNEL_UNAVAILABLE" if geometry is None else "NOT_RECOGNIZED")
        ),
        kernel=OpenCascadeGeometryKernel.name,
        kernel_version=OpenCascadeGeometryKernel.version if geometry is not None else None,
        shape_class=None if geometry is None else geometry.shape_type,
        feature_rule_version="1.0.0",
        feature_count=0 if feature_result is None else len(feature_result.features),
        features=[]
        if feature_result is None
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
            for index, feature in enumerate(feature_result.features, start=1)
        ],
        warnings=(
            ([] if result.feature_warning is None else [result.feature_warning])
            if feature_result is None
            else list(feature_result.warnings)
        ),
        limitations=(
            ["Feature recognition requires available, valid kernel topology."]
            if feature_result is None
            else list(feature_result.limitations)
        ),
        traceability=[
            f"document:{result.document_id}",
            f"kernel:{OpenCascadeGeometryKernel.version}",
            "feature-rule:1.0.0",
        ],
        uncertainty=("UNKNOWN" if feature_result is None else feature_result.uncertainty),
        tolerance=GeometryValue(
            value=None if feature_result is None else feature_result.tolerance,
            unit=analysis.length_unit,
            status="NOT_AVAILABLE" if feature_result is None else "AVAILABLE",
        ),
    )
    topology_evidence = result.topology_evidence
    topology_contract = GeometryTopologyEvidenceContract(
        status="NOT_AVAILABLE" if topology_evidence is None else topology_evidence.status,
        source_sha256=None if topology_evidence is None else topology_evidence.source_sha256,
        kernel=OpenCascadeGeometryKernel.name,
        kernel_version=(None if topology_evidence is None else topology_evidence.kernel_version),
        kernel_binding=OpenCascadeGeometryKernel.binding,
        stable_id_version=(
            "occt-canonical-geometry/v1"
            if topology_evidence is None
            else topology_evidence.stable_id_version
        ),
        source_unit=analysis.length_unit,
        normalized_unit=(None if topology_evidence is None else topology_evidence.normalized_unit),
        normalization_scale=(
            None if topology_evidence is None else topology_evidence.normalization_scale
        ),
        transform=TopologyTransformEvidence(
            representation=(
                "NOT_AVAILABLE"
                if topology_evidence is None
                else topology_evidence.transform_representation
            ),
        ),
        topology_valid=(None if topology_evidence is None else topology_evidence.topology_valid),
        shape_type=None if topology_evidence is None else topology_evidence.shape_type,
        counts={} if topology_evidence is None else topology_evidence.counts,
        elements=[]
        if topology_evidence is None
        else [
            TopologyElementEvidenceResponse(
                element_id=element.element_id,
                kind=element.kind,
                geometry_type=element.geometry_type,
                orientation=element.orientation,
                bounds=element.bounds,
                metrics=element.metrics,
                contained_by=list(element.contained_by),
                contains=list(element.contains),
                adjacent_to=list(element.adjacent_to),
                connected_to=list(element.connected_to),
                ambiguity_group=element.ambiguity_group,
                limitations=list(element.limitations),
            )
            for element in topology_evidence.elements
        ],
        kernel_tolerance=GeometryValue(
            value=None if topology_evidence is None else topology_evidence.kernel_tolerance,
            unit="mm",
            status=(
                "NOT_AVAILABLE"
                if topology_evidence is None or topology_evidence.kernel_tolerance is None
                else "AVAILABLE"
            ),
        ),
        modeling_tolerance=GeometryValue(
            value=(None if topology_evidence is None else topology_evidence.modeling_tolerance_max),
            unit="mm",
            status=(
                "NOT_AVAILABLE"
                if topology_evidence is None or topology_evidence.modeling_tolerance_max is None
                else "AVAILABLE"
            ),
        ),
        manufacturing_tolerance=GeometryValue(
            value=None,
            unit=analysis.length_unit,
            status="NOT_PROVIDED",
        ),
        warnings=(
            ["Topology evidence is unavailable."]
            if topology_evidence is None
            else list(topology_evidence.warnings)
        ),
        unsupported=(
            ["TOPOLOGY_EVIDENCE_EXTRACTION"]
            if topology_evidence is None
            else list(topology_evidence.unsupported)
        ),
        limitations=(
            ["No geometric topology evidence was produced."]
            if topology_evidence is None
            else list(topology_evidence.limitations)
        ),
        provenance=[] if topology_evidence is None else list(topology_evidence.provenance),
        evidence_refs=([] if topology_evidence is None else list(topology_evidence.evidence_refs)),
    )
    return CADAnalysisResponse(
        document_id=result.document_id,
        source_filename=result.source_filename,
        step_filename=analysis.filename,
        schema_name=analysis.schema,
        entity_count=analysis.entity_count,
        entity_types=analysis.entity_types,
        cartesian_point_count=analysis.cartesian_point_count,
        bounding_box=bounding_box,
        length_unit=analysis.length_unit,
        volume=analysis.volume,
        volume_status=analysis.volume_status,
        report=result.report,
        geometry=geometry_contract,
        features=feature_contract,
        topology_evidence=topology_contract,
    )
