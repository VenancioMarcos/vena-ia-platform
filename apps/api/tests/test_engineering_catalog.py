from starlette.testclient import TestClient


def _create(
    client: TestClient,
    headers: dict[str, str],
    kind: str,
    code: str,
    properties: dict[str, object] | None = None,
) -> dict[str, object]:
    response = client.post(
        "/engineering/catalogs",
        headers=headers,
        json={
            "kind": kind,
            "code": code,
            "name": f"Test {kind}",
            "data_version": "2026.08",
            "source": "Owner-supplied engineering catalog fixture",
            "properties": properties or {"unit_system": "METRIC"},
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


def test_deterministic_recommendation_time_cost_and_limits(
    client: TestClient, make_account
) -> None:
    account = make_account(email="engineer@vena-ia.dev")
    material = _create(
        client,
        account.headers,
        "MATERIAL",
        "AL-7075",
        {"cutting_speed_m_min": 180, "feed_per_tooth_mm": 0.05},
    )
    machine = _create(
        client,
        account.headers,
        "MACHINE",
        "MILL-002",
        {"operations": ["milling"], "max_rpm": 12000, "max_feed_mm_min": 5000},
    )
    tool = _create(
        client,
        account.headers,
        "TOOL",
        "EM-8-4F",
        {"operations": ["milling"], "diameter_mm": 8, "teeth": 4},
    )
    response = client.post(
        "/engineering/recommendations/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": machine["id"],
            "tool_id": tool["id"],
            "operation": "milling",
            "cutting_length_mm": 1000,
            "setup_time_min": 15,
            "machine_hour_rate": 120,
            "tool_cost_allocation": 5,
            "currency": "BRL",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["schema_version"] == "vena-ia.engineering-recommendation/v1"
    assert body["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"
    assert body["compatibility"] == "PRELIMINARY_COMPATIBILITY_CHECK:COMPATIBLE"
    assert body["preliminary_parameters"]["spindle_speed"]["unit"] == "rpm"
    assert body["machining_time_estimate"]["status"] == "AVAILABLE"
    assert body["cost_estimate"]["unit"] == "BRL"
    assert "G-code" in body["limitations"][2]
    assert "coordinates" not in str(body).lower()


def test_recommendation_reports_not_available_without_properties(
    client: TestClient, make_account
) -> None:
    account = make_account(email="limited@vena-ia.dev")
    material = _create(client, account.headers, "MATERIAL", "UNKNOWN-MAT")
    machine = _create(client, account.headers, "MACHINE", "UNKNOWN-MACHINE")
    tool = _create(client, account.headers, "TOOL", "UNKNOWN-TOOL")
    response = client.post(
        "/engineering/recommendations/preliminary",
        headers=account.headers,
        json={
            "material_id": material["id"],
            "machine_id": machine["id"],
            "tool_id": tool["id"],
            "operation": "drilling",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["preliminary_parameters"]["spindle_speed"]["status"] == "NOT_AVAILABLE"
    assert body["cost_estimate"]["status"] == "NOT_AVAILABLE"
    assert body["status"] == "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW"


def test_recommendation_requires_authentication(client: TestClient) -> None:
    assert client.post("/engineering/recommendations/preliminary", json={}).status_code == 401
