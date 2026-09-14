import pytest
from pydantic import ValidationError

from app.modules.cnc.schemas import (
    ChipBreakerSafeEnvelope,
    ChipBreakingMachinabilityAuditPayload,
)


def _payload(
    *,
    feed_mm_per_rev: float = 0.25,
    depth_of_cut_mm: float = 2.0,
) -> ChipBreakingMachinabilityAuditPayload:
    inside = 0.15 <= feed_mm_per_rev <= 0.4 and 1.0 <= depth_of_cut_mm <= 4.0
    return ChipBreakingMachinabilityAuditPayload(
        chipbreaker_reference="CNMG_120408_PM_TABULATED",
        feed_mm_per_rev=feed_mm_per_rev,
        depth_of_cut_mm=depth_of_cut_mm,
        uncut_chip_thickness_mm=0.2,
        formed_chip_thickness_mm=0.4,
        chip_compression_ratio=2.0,
        free_chip_length_mm=18.0,
        safe_breaking_envelopes=(
            ChipBreakerSafeEnvelope(
                chipbreaker_reference="CNMG_120408_PM_TABULATED",
                feed_min_mm_per_rev=0.15,
                feed_max_mm_per_rev=0.4,
                depth_of_cut_min_mm=1.0,
                depth_of_cut_max_mm=4.0,
            ),
        ),
        audit_status=(
            "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"
            if inside
            else "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING"
        ),
    )


def test_v2_contract_records_chip_compression_and_tabulated_envelope() -> None:
    audit = _payload()
    assert audit.schema_version == "vena-ia.cnc-chip-breaking-machinability-audit/v2"
    assert audit.chip_compression_ratio == 2.0
    assert audit.free_chip_length_mm == 18.0
    assert audit.audit_status == "CHIP_BREAKING_WITHIN_TABULATED_SAFE_ENVELOPE"
    assert audit.physical_use_authorized is False
    assert audit.automatic_parameter_change_authorized is False
    assert ChipBreakingMachinabilityAuditPayload.model_validate_json(
        audit.model_dump_json()
    ) == audit


def test_feed_or_depth_outside_envelope_produces_warning() -> None:
    assert _payload(feed_mm_per_rev=0.1).audit_status == (
        "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING"
    )
    assert _payload(depth_of_cut_mm=5.0).audit_status == (
        "CHIP_BREAKING_OUTSIDE_TABULATED_SAFE_ENVELOPE_WARNING"
    )


def test_compression_ratio_cannot_be_adulterated() -> None:
    body = _payload().model_dump()
    body["chip_compression_ratio"] = 3.0
    with pytest.raises(ValidationError, match="CHIP_COMPRESSION_RATIO_INCONSISTENT"):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)


def test_unresolved_or_invalid_tabulated_envelope_fails_closed() -> None:
    body = _payload().model_dump()
    body["chipbreaker_reference"] = "UNKNOWN"
    with pytest.raises(
        ValidationError, match="CHIP_BREAKER_SAFE_ENVELOPE_REFERENCE_UNRESOLVED"
    ):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)

    with pytest.raises(ValidationError, match="CHIP_BREAKER_SAFE_ENVELOPE_INVALID"):
        ChipBreakerSafeEnvelope(
            chipbreaker_reference="INVALID",
            feed_min_mm_per_rev=0.4,
            feed_max_mm_per_rev=0.15,
            depth_of_cut_min_mm=1.0,
            depth_of_cut_max_mm=4.0,
        )


def test_physical_or_automatic_authority_cannot_be_promoted() -> None:
    body = _payload().model_dump()
    body["automatic_parameter_change_authorized"] = True
    with pytest.raises(ValidationError):
        ChipBreakingMachinabilityAuditPayload.model_validate(body)
