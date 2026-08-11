from dataclasses import dataclass

from app.modules.cad.evidence import GeometryTopologyEvidence, unavailable_evidence
from app.modules.cad.parser import StepAnalysis, StepTextParser
from app.modules.cad.features import FeatureRecognitionResult, FeatureRecognizer
from app.modules.cad.kernel import GeometryKernelError, KernelGeometry, OpenCascadeGeometryKernel
from app.modules.documents.service import DocumentService, InvalidDocumentError
from app.modules.documents.storage import DocumentStorage, StorageError


class CADContentUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class CADDocumentAnalysis:
    document_id: str
    source_filename: str
    analysis: StepAnalysis
    report: str
    geometry: KernelGeometry | None = None
    geometry_warning: str | None = None
    features: FeatureRecognitionResult | None = None
    feature_warning: str | None = None
    topology_evidence: GeometryTopologyEvidence | None = None


class CADAnalysisService:
    def __init__(
        self,
        documents: DocumentService,
        storage: DocumentStorage,
        parser: StepTextParser,
    ) -> None:
        self._documents = documents
        self._storage = storage
        self._parser = parser

    def analyze(self, document_id: str) -> CADDocumentAnalysis:
        document = self._documents.get(document_id)
        if document.content_type not in {"application/step", "model/step"}:
            raise InvalidDocumentError("Document is not an allowed STEP file")
        try:
            content = self._storage.download_file(document.storage_path)
        except StorageError as exc:
            raise CADContentUnavailableError("CAD document storage unavailable") from exc
        analysis = self._parser.parse(content)
        geometry = None
        geometry_warning = None
        features = None
        feature_warning = None
        topology_evidence = None
        try:
            geometry, features, topology_evidence, feature_warning = (
                OpenCascadeGeometryKernel().analyze_step_with_evidence(
                    content,
                    recognizer=FeatureRecognizer(),
                    unit=analysis.length_unit,
                )
            )
        except GeometryKernelError as exc:
            geometry_warning = str(exc)
            topology_evidence = unavailable_evidence(
                content,
                analysis.length_unit,
                kernel=OpenCascadeGeometryKernel.name,
                kernel_version=OpenCascadeGeometryKernel.version,
                kernel_binding=OpenCascadeGeometryKernel.binding,
                warning=str(exc),
            )
        dimensions = (
            "unavailable"
            if analysis.bounding_box is None
            else " × ".join(f"{value:g}" for value in analysis.bounding_box.dimensions)
        )
        report = (
            f"STEP schema: {analysis.schema or 'unknown'}. "
            f"Entities: {analysis.entity_count}. "
            f"Cartesian points: {analysis.cartesian_point_count}. "
            f"Envelope dimensions: {dimensions} {analysis.length_unit}. "
            "Volume is unavailable without a validated geometry kernel."
        )
        return CADDocumentAnalysis(
            document_id=document.id,
            source_filename=document.filename,
            analysis=analysis,
            report=report,
            geometry=geometry,
            geometry_warning=geometry_warning,
            features=features,
            feature_warning=feature_warning,
            topology_evidence=topology_evidence,
        )
