from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.cad.dependencies import get_cad_analysis_service
from app.modules.cad.parser import BoundingBox, StepAnalysis, StepParseError, StepTextParser
from app.modules.cad.service import CADAnalysisService, CADDocumentAnalysis
from app.modules.cad.service import CADContentUnavailableError
from app.modules.documents.models import Document
from app.modules.documents.dependencies import get_document_storage
from app.modules.documents.service import DocumentNotFoundError, InvalidDocumentError

STEP = b"""ISO-10303-21;
HEADER;
FILE_NAME('fixture.step','2026-07-30T00:00:00',('Vena'),('Vena'),'','','');
FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF'));
ENDSEC;
DATA;
#1=CARTESIAN_POINT('',(0.,-2.,1.));
#2=CARTESIAN_POINT('',(10.,8.,6.));
#3=SI_UNIT(.MILLI.,.METRE.);
ENDSEC;
END-ISO-10303-21;
"""


def test_step_parser_extracts_metadata_and_envelope() -> None:
    result = StepTextParser().parse(STEP)

    assert result.filename == "fixture.step"
    assert result.schema == "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF"
    assert result.entity_count == 3
    assert result.cartesian_point_count == 2
    assert result.length_unit == "mm"
    assert result.bounding_box is not None
    assert result.bounding_box.minimum == (0.0, -2.0, 1.0)
    assert result.bounding_box.maximum == (10.0, 8.0, 6.0)
    assert result.bounding_box.dimensions == (10.0, 10.0, 5.0)
    assert result.volume is None


def test_step_parser_rejects_missing_terminator() -> None:
    with pytest.raises(StepParseError, match="terminator"):
        StepTextParser().parse(b"ISO-10303-21;")


def test_step_parser_rejects_binary_content() -> None:
    with pytest.raises(StepParseError, match="binary"):
        StepTextParser().parse(b"ISO-10303-21;\x00END-ISO-10303-21;")


def test_step_parser_supports_scientific_d_notation_and_no_points() -> None:
    scientific = STEP.replace(b"(10.,8.,6.)", b"(1.0D+1,-8.0E+0,.6E1)")
    result = StepTextParser().parse(scientific)
    assert result.bounding_box is not None
    assert result.bounding_box.maximum == (10.0, -2.0, 6.0)

    no_points = (
        b"ISO-10303-21;\nHEADER;\nENDSEC;\nDATA;\n"
        b"#1=SI_UNIT(.MILLI.,.METRE.);\nENDSEC;\nEND-ISO-10303-21;"
    )
    empty = StepTextParser().parse(no_points)
    assert empty.bounding_box is None
    assert empty.cartesian_point_count == 0


def test_cad_service_checks_access_and_downloads_document() -> None:
    documents = MagicMock()
    documents.get.return_value = Document(
        id="document",
        project_id="project",
        filename="fixture.step",
        content_type="application/step",
        file_size=len(STEP),
        storage_path="projects/project/documents/document/fixture.step",
        status="UPLOADED",
    )
    storage = MagicMock()
    storage.download_file.return_value = STEP
    service = CADAnalysisService(documents, storage, StepTextParser())

    result = service.analyze("document")

    documents.get.assert_called_once_with("document")
    storage.download_file.assert_called_once_with(
        "projects/project/documents/document/fixture.step"
    )
    assert "Envelope dimensions: 10 × 10 × 5 mm" in result.report


def test_cad_route_serializes_preliminary_analysis(client: TestClient) -> None:
    service = MagicMock()
    service.analyze.return_value = CADDocumentAnalysis(
        document_id="document",
        source_filename="fixture.step",
        analysis=StepAnalysis(
            filename="fixture.step",
            schema="AP242",
            entity_count=3,
            entity_types={"CARTESIAN_POINT": 2, "SI_UNIT": 1},
            cartesian_point_count=2,
            bounding_box=BoundingBox(
                minimum=(0.0, 0.0, 0.0),
                maximum=(10.0, 5.0, 2.0),
            ),
            length_unit="mm",
            volume=None,
            volume_status="UNAVAILABLE_WITHOUT_GEOMETRY_KERNEL",
        ),
        report="Preliminary report.",
    )
    app.dependency_overrides[get_cad_analysis_service] = lambda: service
    try:
        response = client.post("/cad/documents/document/analysis")
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["bounding_box"]["dimensions"] == [10.0, 5.0, 2.0]
    assert payload["volume"] is None
    assert payload["volume_status"] == "UNAVAILABLE_WITHOUT_GEOMETRY_KERNEL"


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (StepParseError("invalid"), 422),
        (DocumentNotFoundError("missing"), 404),
        (InvalidDocumentError("wrong type"), 400),
        (CADContentUnavailableError("storage unavailable"), 503),
    ],
)
def test_cad_route_maps_parser_error(
    client: TestClient,
    error: Exception,
    expected_status: int,
) -> None:
    service = MagicMock()
    service.analyze.side_effect = error
    app.dependency_overrides[get_cad_analysis_service] = lambda: service
    try:
        response = client.post("/cad/documents/document/analysis")
    finally:
        app.dependency_overrides.pop(get_cad_analysis_service, None)
    assert response.status_code == expected_status


def test_cad_analysis_hides_other_owners_document(
    client: TestClient,
    make_account,
) -> None:
    storage = MagicMock()
    storage.download_file.return_value = STEP
    app.dependency_overrides[get_document_storage] = lambda: storage
    try:
        owner = make_account("cad-owner-route@vena-ia.dev")
        project = client.post(
            "/projects",
            headers=owner.headers,
            json={"name": "CAD Project"},
        ).json()
        uploaded = client.post(
            f"/projects/{project['id']}/documents",
            headers=owner.headers,
            files={"file": ("part.step", STEP, "application/step")},
        ).json()
        outsider = make_account("cad-outsider@vena-ia.dev")

        response = client.post(
            f"/cad/documents/{uploaded['id']}/analysis",
            headers=outsider.headers,
        )
    finally:
        app.dependency_overrides.pop(get_document_storage, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
    storage.download_file.assert_not_called()
