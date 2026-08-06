from starlette.testclient import TestClient


def _create(client: TestClient, headers: dict[str, str], kind: str, code: str) -> dict[str, object]:
    response = client.post(
        "/engineering/catalogs",
        headers=headers,
        json={
            "kind": kind,
            "code": code,
            "name": f"Test {kind}",
            "data_version": "2026.08",
            "source": "Owner-supplied engineering catalog fixture",
            "properties": {"unit_system": "METRIC"},
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_catalog_requires_authentication(client: TestClient) -> None:
    assert client.get("/engineering/catalogs").status_code == 401


def test_versioned_catalog_and_preliminary_selection(client: TestClient, make_account) -> None:
    account = make_account()
    material = _create(client, account.headers, "MATERIAL", "AL-6061-T6")
    machine = _create(client, account.headers, "MACHINE", "MILL-001")
    tool = _create(client, account.headers, "TOOL", "EM-10-4F")

    listed = client.get("/engineering/catalogs?kind=MATERIAL", headers=account.headers)
    assert listed.status_code == 200
    assert [item["code"] for item in listed.json()] == ["AL-6061-T6"]
    assert listed.json()[0]["schema_version"] == "vena-ia.engineering-catalog/v1"

    selected = client.post(
        "/engineering/selections/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": machine["id"],
            "tool_id": tool["id"],
            "operation": "MILLING",
        },
    )
    assert selected.status_code == 200, selected.text
    body = selected.json()
    assert body["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    assert len(body["traceability"]) == 3
    assert "G-code" in body["limitations"][0]


def test_selection_rejects_wrong_catalog_kind(client: TestClient, make_account) -> None:
    account = make_account(email="other@vena-ia.dev")
    material = _create(client, account.headers, "MATERIAL", "STEEL-1018")
    response = client.post(
        "/engineering/selections/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": material["id"],
            "tool_id": material["id"],
            "operation": "MILLING",
        },
    )
    assert response.status_code == 404
