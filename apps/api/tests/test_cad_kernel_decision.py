from starlette.testclient import TestClient

from app.modules.cad.schemas import GeometryAnalysisContract, GeometryValue


def test_kernel_decision_requires_authentication(client: TestClient) -> None:
    assert client.get("/cad/kernel-decision").status_code == 401


def test_kernel_decision_is_restricted_and_versioned(client: TestClient, make_account) -> None:
    account = make_account(email="cad-reviewer@vena-ia.dev")
    response = client.get("/cad/kernel-decision", headers=account.headers)
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "B_APPROVED_WITH_RESTRICTIONS"
    assert body["integration_status"] == "NOT_INSTALLED_PACKAGE_1_DECISION_ONLY"
    assert body["contract_schema"] == "vena-ia.geometry-analysis/v1"


def test_geometry_contract_represents_unavailable_kernel_results() -> None:
    value = GeometryValue(value=None, unit="mm3", status="NOT_AVAILABLE")
    contract = GeometryAnalysisContract(
        status="PRELIMINARY_REQUIRES_VALIDATED_KERNEL",
        unit="mm",
        bounding_box=None,
        surface_area=GeometryValue(value=None, unit="mm2", status="NOT_AVAILABLE"),
        volume=value,
        topology_valid=None,
        tolerance=GeometryValue(value=None, unit="mm", status="NOT_AVAILABLE"),
        entity_count=0,
        warnings=["Kernel not integrated"],
        uncertainty="UNKNOWN",
        traceability=["synthetic-contract-test"],
        kernel="NONE",
        kernel_version=None,
        limitations=["No manufacturability claim"],
    )
    assert contract.schema_version == "vena-ia.geometry-analysis/v1"
    assert contract.volume.status == "NOT_AVAILABLE"
