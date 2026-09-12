from __future__ import annotations

import hashlib
from collections.abc import Generator
from pathlib import Path
from typing import BinaryIO

import pytest
from starlette.testclient import TestClient

from app.main import app
from app.modules.documents.dependencies import get_document_storage


class InMemoryDocumentStorage:
    """Test-only storage that exercises upload and subsequent CAD download unchanged."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def initialize(self) -> None:
        return None

    def upload_file(
        self,
        storage_path: str,
        data: BinaryIO,
        file_size: int,
        content_type: str,
    ) -> None:
        del content_type
        content = data.read()
        assert len(content) == file_size
        self.objects[storage_path] = content

    def download_file(self, storage_path: str) -> bytes:
        return self.objects[storage_path]

    def delete_file(self, storage_path: str) -> None:
        self.objects.pop(storage_path, None)

    def file_exists(self, storage_path: str) -> bool:
        return storage_path in self.objects


@pytest.fixture()
def real_cad_storage() -> Generator[InMemoryDocumentStorage, None, None]:
    storage = InMemoryDocumentStorage()
    app.dependency_overrides[get_document_storage] = lambda: storage
    yield storage
    app.dependency_overrides.pop(get_document_storage, None)


def _cylinder_step(tmp_path: Path) -> bytes:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path = tmp_path / "first-controlled-cylinder.step"
    writer = STEPControl_Writer()
    writer.Transfer(BRepPrimAPI_MakeCylinder(10, 30).Shape(), STEPControl_AsIs)
    assert writer.Write(str(path)) == IFSelect_RetDone
    return path.read_bytes()


def _catalog(
    client: TestClient,
    headers: dict[str, str],
    organization_id: str,
    kind: str,
    code: str,
    properties: dict[str, object],
) -> str:
    response = client.post(
        f"/engineering/catalogs?organization_id={organization_id}",
        headers=headers,
        json={
            "kind": kind,
            "code": code,
            "name": code,
            "data_version": "first-controlled-test-v1",
            "source": "Explicit test-only organization catalog input",
            "properties": properties,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_real_step_upload_reaches_controlled_candidate_download(
    client: TestClient,
    make_account,
    real_cad_storage: InMemoryDocumentStorage,
    tmp_path: Path,
) -> None:
    owner = make_account("first-controlled-test@vena-ia.dev")
    project = client.post(
        "/projects", headers=owner.headers, json={"name": "First controlled CAD test"}
    )
    assert project.status_code == 201, project.text
    organization = client.post(
        "/organizations", headers=owner.headers, json={"name": "Controlled CAD test"}
    )
    assert organization.status_code == 201, organization.text
    organization_id = organization.json()["id"]

    content = _cylinder_step(tmp_path)
    upload = client.post(
        f"/projects/{project.json()['id']}/documents",
        headers=owner.headers,
        files={"file": ("first-controlled-cylinder.step", content, "application/step")},
    )
    assert upload.status_code == 201, upload.text
    assert next(iter(real_cad_storage.objects.values())) == content

    material_id = _catalog(
        client,
        owner.headers,
        organization_id,
        "MATERIAL",
        "TEST-STEEL",
        {"cutting_speed_m_min": 150, "feed_per_tooth_mm": 0.05},
    )
    machine_id = _catalog(
        client,
        owner.headers,
        organization_id,
        "MACHINE",
        "TEST-3AXIS-MILL",
        {"operations": ["milling"], "max_rpm": 10_000, "max_feed_mm_min": 4_000},
    )
    tool_id = _catalog(
        client,
        owner.headers,
        organization_id,
        "TOOL",
        "TEST-END-MILL",
        {"operations": ["milling"], "diameter_mm": 0.5, "teeth": 2},
    )
    run = client.post(
        "/engineering/controlled-environment/runs",
        headers=owner.headers,
        json={
            "organization_id": organization_id,
            "planning": {
                "document_id": upload.json()["id"],
                "stock": {
                    "status": "PROVIDED",
                    "minimum": [-11, -11, -1],
                    "maximum": [11, 11, 31],
                    "unit": "mm",
                    "source_ref": "explicit-test-stock-bounds",
                },
                "manufacturing_intent": "milling",
                "material_id": material_id,
                "machine_id": machine_id,
                "tool_id": tool_id,
                "fixture": "Synthetic fixture statement requiring human confirmation",
                "datum_wcs_input": "Candidate WCS requiring human confirmation",
            },
            "tool": {"tool_id": tool_id, "diameter_mm": 0.5, "flute_length_mm": 10},
            "machine_minimum": [-100, -100, -10],
            "machine_maximum": [100, 100, 100],
            "clearance_z_mm": 40,
            "retract_z_mm": 35,
            "feed_mm_min": 800,
            "fixture_keep_outs": [],
            "holdout_id": "first-controlled-test-sealed-reference",
            "sealed_reference_hash": hashlib.sha256(
                b"independent external reference placeholder; no expected features"
            ).hexdigest(),
            "questions_asked": ["Can G0-G8 be reproduced from the uploaded CAD evidence?"],
        },
    )
    assert run.status_code == 200, run.text
    result = run.json()
    assert result["status"] == "READY_FOR_CONTROLLED_DOWNLOAD"
    assert result["manufacturing_model"]["final_geometry"]["topology_valid"] is True
    assert result["manufacturing_model"]["verification"]["coherent"] is True
    assert result["toolpath"]["status"] == "CANDIDATE_FOR_VALIDATION"
    assert result["level2_evidence"]["status"] == "PASS_REQUIRES_HUMAN_REVIEW"
    assert all(
        gate["status"] == "PASS"
        for gate in result["blind_validation"]["gates"]
        if gate["gate"] != "G9"
    )
    assert next(
        gate for gate in result["blind_validation"]["gates"] if gate["gate"] == "G9"
    )["status"] == "PENDING_REVIEW"
    assert result["digital_thread"]["status"] == "COMPLETE_NON_PRODUCTION"
    assert result["g9_state"] == "PENDING_AUTHORITATIVE_REVIEW"
    assert result["physical_use_authorized"] is False

    download = client.post(
        "/engineering/controlled-environment/download",
        headers=owner.headers,
        json={
            "organization_id": organization_id,
            "gcode_candidate": result["gcode_candidate"],
            "blind_validation": result["blind_validation"],
            "digital_thread": result["digital_thread"],
            "download_token": result["download_token"],
        },
    )
    assert download.status_code == 200, download.text
    assert download.headers["x-vena-ia-classification"] == "CANDIDATE_FOR_VALIDATION"
    assert download.headers["x-vena-ia-physical-use-authorized"] == "false"
    assert download.headers["x-vena-ia-review-state"] == "REQUIRES_HUMAN_REVIEW"
    assert download.text == result["gcode_candidate"]["program"]
    assert "M30" in download.text
    assert all(command not in download.text for command in ("M03", "M04", "M06"))
