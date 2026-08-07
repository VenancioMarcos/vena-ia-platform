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
        integration_status="NOT_INSTALLED_PACKAGE_1_DECISION_ONLY",
        official_python="3.13.11",
        experimental_python="3.14.6",
        contract_schema="vena-ia.geometry-analysis/v1",
        limitations=[
            "Binary/package compatibility must pass Windows, Linux and Docker gates.",
            "No topology, area or volume claim is made before controlled integration.",
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
    )
