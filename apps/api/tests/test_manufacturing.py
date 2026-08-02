import pytest
from starlette.testclient import TestClient
from pydantic import ValidationError

from app.modules.manufacturing.schemas import MaterialFamily, MillingInput
from app.modules.manufacturing.service import MillingRecommendationService


def test_milling_recommendation_applies_machine_limits() -> None:
    result = MillingRecommendationService().recommend(
        MillingInput(
            material=MaterialFamily.ALUMINUM,
            tool_diameter_mm=10,
            tool_teeth=4,
            cutting_length_mm=1000,
            machine_max_rpm=6000,
            machine_max_feed_mm_min=1000,
        )
    )

    assert result.spindle_rpm == 6000
    assert result.feed_mm_min == 1000
    assert result.estimated_cutting_time_min == 1
    assert result.limiting_factors == ["MACHINE_MAX_RPM", "MACHINE_MAX_FEED"]
    assert result.status == "PRELIMINARY_REQUIRES_HUMAN_REVIEW"


@pytest.mark.parametrize(
    "material",
    list(MaterialFamily),
)
def test_rules_cover_supported_materials(material: MaterialFamily) -> None:
    result = MillingRecommendationService().recommend(
        MillingInput(
            material=material,
            tool_diameter_mm=12,
            tool_teeth=4,
            cutting_length_mm=200,
            machine_max_rpm=12_000,
            machine_max_feed_mm_min=5_000,
        )
    )
    assert result.feed_mm_min > 0
    assert result.estimated_cutting_time_min > 0


def test_recommendation_without_machine_limitation() -> None:
    result = MillingRecommendationService().recommend(
        MillingInput(
            material=MaterialFamily.CARBON_STEEL,
            tool_diameter_mm=20,
            tool_teeth=2,
            cutting_length_mm=200,
            machine_max_rpm=50_000,
            machine_max_feed_mm_min=50_000,
        )
    )
    assert result.limiting_factors == []
    assert len(result.warnings) == 4
    assert result.calculation_basis


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), float("-inf")])
def test_rejects_non_finite_inputs(invalid: float) -> None:
    with pytest.raises(ValidationError):
        MillingInput(
            material=MaterialFamily.CARBON_STEEL,
            tool_diameter_mm=invalid,
            tool_teeth=4,
            cutting_length_mm=100,
            machine_max_rpm=8000,
            machine_max_feed_mm_min=2000,
        )


def test_manufacturing_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/manufacturing/milling/recommendation",
        json={
            "material": "CARBON_STEEL",
            "tool_diameter_mm": 10,
            "tool_teeth": 4,
            "cutting_length_mm": 500,
            "machine_max_rpm": 8000,
            "machine_max_feed_mm_min": 2000,
        },
    )
    assert response.status_code == 401


def test_manufacturing_endpoint_returns_review_gated_result(
    client: TestClient,
    make_account,
) -> None:
    account = make_account("cam-engineer@vena-ia.dev")
    response = client.post(
        "/manufacturing/milling/recommendation",
        headers=account.headers,
        json={
            "material": "CARBON_STEEL",
            "tool_diameter_mm": 10,
            "tool_teeth": 4,
            "cutting_length_mm": 500,
            "machine_max_rpm": 8000,
            "machine_max_feed_mm_min": 2000,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PRELIMINARY_REQUIRES_HUMAN_REVIEW"
    assert "gcode" not in response.text.lower()
