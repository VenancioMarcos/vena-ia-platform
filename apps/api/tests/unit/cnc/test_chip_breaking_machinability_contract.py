import math

import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import ChipBreakingMachinabilityAuditPayload
from app.modules.cnc.services.chip_breaking_auditor import (
    audit_chip_breaking_machinability,
)


def _audit(
    *,
    material_reference: str = "Aço ABNT 1045",
    chipbreaker_reference: str = "CNMG_120408_PM_TABULATED",
    feed_mm_per_rev: float = 0.25,
    depth_of_cut_mm: float = 2.0,
    rake_angle_deg: float = 6.0,
) -> ChipBreakingMachinabilityAuditPayload:
    return audit_chip_breaking_machinability(
        material_reference,
        chipbreaker_reference=chipbreaker_reference,
        feed_mm_per_rev=feed_mm_per_rev,
        depth_of_cut_mm=depth_of_cut_mm,
        insert_nose_radius_mm=0.8,
        cutting_edge_angle_deg=95.0,
        rake_angle_deg=rake_angle_deg,
    )


def test_service_calculates_uncut_thickness_width_and_compression_ratio() -> None:
    audit = _audit()
    sin_kr = math.sin(math.radians(95.0))

    assert audit.schema_version == "vena-ia.cnc-chip-breaking-machinability-audit/v2"
    assert audit.material_profile == "ABNT_1045"
    assert audit.chipbreaker_family == "PM"
    assert audit.uncut_chip_thickness_mm == pytest.approx(0.25 * sin_kr)
    assert audit.chip_width_mm == pytest.approx(2.0 / sin_kr)
    assert audit.chip_compression_ratio == pytest.approx(2.4)
    assert audit.formed_chip_thickness_mm == pytest.approx(0.25 * sin_kr * 2.4)
    assert audit.audit_status == "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"
    assert audit.physical_use_authorized is False
    assert audit.automatic_parameter_change_authorized is False
    assert ChipBreakingMachinabilityAuditPayload.model_validate_json(
        audit.model_dump_json()
    ) == audit


@pytest.mark.parametrize(
    ("material", "expected_ratio"),
    [
        ("AISI 1020", 2.2),
        ("Aço ABNT 1045", 2.4),
        ("Alumínio 6061-T6", 1.8),
    ],
)
def test_material_table_drives_chip_compression_ratio(
    material: str,
    expected_ratio: float,
) -> None:
    assert _audit(material_reference=material).chip_compression_ratio == pytest.approx(
        expected_ratio
    )


def test_positive_rake_reduces_tabulated_compression_ratio() -> None:
    assert _audit(rake_angle_deg=16.0).chip_compression_ratio == pytest.approx(2.2)


@pytest.mark.parametrize(
    "chipbreaker_reference",
    [
        "CNMG_120408_PM_TABULATED",
        "CNMG_120408_PR_TABULATED",
        "CNMG_120408_PF_TABULATED",
    ],
)
def test_known_chipbreaker_geometries_resolve_declared_envelopes(
    chipbreaker_reference: str,
) -> None:
    family = chipbreaker_reference.rsplit("_", 2)[-2]
    audit = _audit(
        chipbreaker_reference=chipbreaker_reference,
        feed_mm_per_rev={"PM": 0.25, "PR": 0.35, "PF": 0.10}[family],
        depth_of_cut_mm={"PM": 2.0, "PR": 3.0, "PF": 1.0}[family],
    )
    assert audit.audit_status == "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"


@pytest.mark.parametrize(
    ("feed", "depth"),
    [(0.10, 2.0), (0.70, 2.0), (0.25, 0.5), (0.25, 5.0)],
)
def test_outside_feed_or_depth_warns_fail_closed(feed: float, depth: float) -> None:
    audit = _audit(feed_mm_per_rev=feed, depth_of_cut_mm=depth)
    assert audit.audit_status == (
        "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING"
    )


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"feed_mm_per_rev": 0.0}, "CHIP_BREAKING_FEED_INVALID"),
        ({"depth_of_cut_mm": -1.0}, "CHIP_BREAKING_DEPTH_INVALID"),
        ({"feed_mm_per_rev": math.nan}, "CHIP_BREAKING_FEED_INVALID"),
        ({"rake_angle_deg": math.inf}, "CHIP_BREAKING_RAKE_ANGLE_INVALID"),
        ({"chipbreaker_reference": "UNKNOWN"}, "CHIP_BREAKER_GEOMETRY_UNSUPPORTED"),
    ],
)
def test_invalid_parameters_or_geometry_fail_closed(
    updates: dict[str, object],
    code: str,
) -> None:
    kwargs: dict[str, object] = {
        "material_reference": "Aço ABNT 1045",
        "chipbreaker_reference": "CNMG_120408_PM_TABULATED",
        "feed_mm_per_rev": 0.25,
        "depth_of_cut_mm": 2.0,
        "insert_nose_radius_mm": 0.8,
        "cutting_edge_angle_deg": 95.0,
        "rake_angle_deg": 6.0,
    }
    kwargs.update(updates)
    with pytest.raises(ValueError, match=code):
        audit_chip_breaking_machinability(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("chip_compression_ratio", 3.0, "CHIP_COMPRESSION_RATIO_INCONSISTENT"),
        ("uncut_chip_thickness_mm", 0.1, "CHIP_BREAKING_UNCUT_THICKNESS_INCONSISTENT"),
        ("chip_width_mm", 99.0, "CHIP_BREAKING_WIDTH_INCONSISTENT"),
        ("free_chip_length_mm", 99.0, "CHIP_BREAKING_FREE_LENGTH_INCONSISTENT"),
        ("chipbreaker_family", "PF", "CHIP_BREAKER_FAMILY_INCONSISTENT"),
    ],
)
def test_replayed_contract_rejects_tampered_analytical_values(
    field: str,
    value: object,
    code: str,
) -> None:
    body = _audit().model_dump()
    body[field] = value
    with pytest.raises(ValidationError, match=code):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)


def test_replayed_contract_rejects_tampered_tabulated_envelope() -> None:
    body = _audit().model_dump()
    body["safe_breaking_envelopes"][0]["feed_min_mm_per_rev"] = 0.01
    with pytest.raises(
        ValidationError,
        match="CHIP_BREAKER_SAFE_ENVELOPE_TABLE_INCONSISTENT",
    ):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)


def test_physical_or_automatic_authority_cannot_be_promoted() -> None:
    body = _audit().model_dump()
    body["automatic_parameter_change_authorized"] = True
    with pytest.raises(ValidationError):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)

    body = _audit().model_dump()
    body["physical_use_authorized"] = True
    with pytest.raises(ValidationError):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)
