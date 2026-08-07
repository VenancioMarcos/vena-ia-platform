from starlette.testclient import TestClient


def _payload() -> dict[str, object]:
    return {
        "operation": "DRILLING",
        "tool_number": 7,
        "spindle_rpm": 2500,
        "feed_mm_min": 300,
        "clearance_z_mm": 20,
    }


def test_cnc_preview_requires_authentication(client: TestClient) -> None:
    assert client.post("/cnc/plan/preview", json=_payload()).status_code == 401


def test_cnc_preview_is_never_executable(client: TestClient, make_account) -> None:
    account = make_account("cnc-review@vena-ia.dev")
    response = client.post(
        "/cnc/plan/preview",
        headers=account.headers,
        json=_payload(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW"
    assert payload["executable_output"] is False
    assert payload["controller_family"] == "FANUC_OI_STRATEGY_PLACEHOLDER"
    assert payload["machine_profile"] == "ROMI_D1250_PLANNED_COMPATIBILITY"
    assert "gcode" not in response.text.lower()


def test_cnc_preview_rejects_unsafe_numeric_inputs(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("cnc-invalid@vena-ia.dev")
    payload = _payload()
    payload["clearance_z_mm"] = 0
    response = client.post(
        "/cnc/plan/preview",
        headers=account.headers,
        json=payload,
    )
    assert response.status_code == 422


def test_cnc_preview_rejects_executable_fields(client: TestClient, make_account) -> None:
    account = make_account("cnc-executable@vena-ia.dev")
    for forbidden in ("gcode", "mcode", "toolpath", "nc_file", "transmission_target"):
        payload = _payload()
        payload[forbidden] = "forbidden"
        response = client.post(
            "/cnc/plan/preview",
            headers=account.headers,
            json=payload,
        )
        assert response.status_code == 422
