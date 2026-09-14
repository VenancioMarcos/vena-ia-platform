import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import GuidewayLoadAuditPayload
from app.modules.cnc.services.guideway_load_auditor import (
    GuidewayLoadAuditError,
    audit_guideway_load,
)
from app.modules.cnc.services.power_force_estimator import estimate_cutting_power_force


def _kienzle(
    *,
    feed_mm_per_rev: float = 0.30,
    depth_of_cut_mm: float = 3.0,
    cutting_edge_angle_deg: float = 95.0,
):
    return estimate_cutting_power_force(
        "ABNT 1045",
        feed_mm_per_rev=feed_mm_per_rev,
        depth_of_cut_mm=depth_of_cut_mm,
        cutting_edge_angle_deg=cutting_edge_angle_deg,
        cutting_speed_m_per_min=180.0,
        spindle_rpm_reference=1_200.0,
        max_spindle_rpm=6_000.0,
        machine_power_limit_kw=30.0,
    )


def _audit(**overrides: object):
    values: dict[str, object] = {
        "source_power_force_audit": _kienzle(),
        "feed_force_ratio": 0.30,
        "radial_force_ratio": 0.50,
        "lever_arm_x_mm": 120.0,
        "lever_arm_y_mm": 180.0,
        "lever_arm_z_mm": 220.0,
        "block_spacing_x_mm": 240.0,
        "rail_spacing_y_mm": 300.0,
        "block_spacing_z_mm": 360.0,
        "static_capacity_n": 80_000.0,
    }
    values.update(overrides)
    return audit_guideway_load(**values)  # type: ignore[arg-type]


def test_roughing_pass_resolves_three_moments_and_maximum_block_load() -> None:
    audit = _audit()
    fc = audit.source_power_force_audit.fc_nominal_n
    ff = fc * 0.30
    fr = fc * 0.50
    expected_pitch = (ff * 220.0 + fc * 120.0) / 1_000.0
    expected_yaw = (ff * 180.0 + fr * 220.0) / 1_000.0
    expected_roll = (fr * 180.0 + fc * 220.0) / 1_000.0
    direct = math.sqrt(fc**2 + ff**2 + fr**2) / 4.0
    expected_max = (
        direct
        + expected_pitch * 1_000.0 / (2.0 * 360.0)
        + expected_yaw * 1_000.0 / (2.0 * 240.0)
        + expected_roll * 1_000.0 / (2.0 * 300.0)
    )

    assert audit.tangential_cutting_force_n == pytest.approx(fc)
    assert audit.axial_feed_force_n == pytest.approx(ff)
    assert audit.radial_cutting_force_n == pytest.approx(fr)
    assert audit.pitching_moment_nm == pytest.approx(expected_pitch)
    assert audit.yawing_moment_nm == pytest.approx(expected_yaw)
    assert audit.rolling_moment_nm == pytest.approx(expected_roll)
    assert audit.max_block_load_n == pytest.approx(expected_max)
    assert audit.load_ratio_percent == pytest.approx(expected_max / 80_000.0 * 100.0)
    assert audit.guideway_status == "GUIDEWAY_LOAD_COMPLIANT"
    assert audit.is_theoretical_model is True
    assert audit.physical_use_authorized is False
    assert GuidewayLoadAuditPayload.model_validate_json(audit.model_dump_json()) == audit


def test_heavy_cut_with_excessive_turret_overhang_warns() -> None:
    audit = _audit(
        source_power_force_audit=_kienzle(feed_mm_per_rev=0.8, depth_of_cut_mm=8.0),
        lever_arm_x_mm=900.0,
        lever_arm_y_mm=900.0,
        lever_arm_z_mm=1_200.0,
        static_capacity_n=30_000.0,
    )

    assert audit.max_block_load_n > 0.5 * audit.static_capacity_n
    assert audit.load_ratio_percent > 50.0
    assert audit.guideway_status == "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("lever_arm_x_mm", 0.0, "GUIDEWAY_LEVER_ARM_X_INVALID"),
        ("block_spacing_x_mm", 0.0, "GUIDEWAY_BLOCK_SPACING_X_INVALID"),
        ("rail_spacing_y_mm", -1.0, "GUIDEWAY_RAIL_SPACING_Y_INVALID"),
        ("block_spacing_z_mm", None, "GUIDEWAY_BLOCK_SPACING_Z_INVALID"),
        ("static_capacity_n", None, "GUIDEWAY_STATIC_CAPACITY_INVALID"),
        ("static_capacity_n", 0.0, "GUIDEWAY_STATIC_CAPACITY_INVALID"),
    ],
)
def test_invalid_geometry_or_machine_capacity_fails_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(GuidewayLoadAuditError, match=code):
        _audit(**{field: value})


def test_invalid_kienzle_force_snapshot_fails_closed() -> None:
    source = _kienzle().model_copy(update={"fc_nominal_n": 10_000_001.0})
    with pytest.raises(
        GuidewayLoadAuditError,
        match="GUIDEWAY_KIENZLE_SOURCE_INVALID",
    ):
        _audit(source_power_force_audit=source)


def test_valid_kienzle_snapshot_above_force_envelope_fails_closed() -> None:
    source = _kienzle(
        feed_mm_per_rev=5.0,
        depth_of_cut_mm=100.0,
        cutting_edge_angle_deg=0.001,
    )
    assert source.fc_nominal_n > 10_000_000.0
    with pytest.raises(
        GuidewayLoadAuditError,
        match="GUIDEWAY_TANGENTIAL_FORCE_OUTSIDE_PHYSICAL_ENVELOPE",
    ):
        _audit(source_power_force_audit=source)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("pitching_moment_nm", 1.0, "GUIDEWAY_PITCHING_MOMENT_INCONSISTENT"),
        ("max_block_load_n", 1.0, "GUIDEWAY_MAX_BLOCK_LOAD_INCONSISTENT"),
        ("load_ratio_percent", 1.0, "GUIDEWAY_LOAD_RATIO_INCONSISTENT"),
        (
            "guideway_status",
            "GUIDEWAY_DYNAMIC_OVERLOAD_WARNING",
            "GUIDEWAY_STATUS_INCONSISTENT",
        ),
    ],
)
def test_replayed_contract_rejects_tampered_derivatives(
    field: str,
    value: object,
    code: str,
) -> None:
    body = _audit().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        GuidewayLoadAuditPayload.model_validate(body)
