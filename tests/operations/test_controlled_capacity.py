import json
from pathlib import Path

import pytest

from scripts.capacity_harness import (
    EVIDENCE_SCHEMA,
    build_evidence,
    deterministic_operation,
    exercise_shared_state,
    load_profile,
    run_controlled_load,
    run_short_soak,
    validate_profile,
    write_evidence,
)
from scripts.capacity_policy import validate_repository

ROOT = Path(__file__).resolve().parents[2]


def test_capacity_profile_and_repository_policy_are_valid() -> None:
    profile = load_profile(ROOT / "capacity-profile.json")
    assert validate_profile(profile) == []
    assert validate_repository(ROOT) == []


def test_invalid_profile_fails_closed() -> None:
    profile = load_profile(ROOT / "capacity-profile.json")
    profile["load"]["concurrency"] = 0
    profile["ai_provider"] = "external"
    errors = validate_profile(profile)
    assert any("concurrency" in error for error in errors)
    assert any("external AI" in error for error in errors)


def test_controlled_load_has_no_loss_and_reports_separate_percentiles() -> None:
    result = run_controlled_load(deterministic_operation, operations=200, concurrency=4)
    assert result["successes"] == 200
    assert result["failures"] == 0
    assert result["p50_ms"] <= result["p95_ms"] <= result["p99_ms"]
    assert result["throughput_observed_per_second"] > 0


def test_short_soak_is_bounded_and_cleans_up() -> None:
    result = run_short_soak(deterministic_operation, 0.1)
    assert result["operations"] > 0
    assert result["failures"] == 0
    assert result["jobs_non_terminal"] == 0
    assert result["queue_final"] == 0
    assert result["cleanup"] is True


def test_two_logical_apis_and_workers_share_unique_claim_state() -> None:
    result = exercise_shared_state(500)
    assert result == {
        "logical_api_instances": 2,
        "workers": 2,
        "submitted": 500,
        "unique_claims": 500,
        "duplicates": 0,
        "queue_final": 0,
        "recovered_after_saturation": True,
    }


def test_capacity_evidence_is_safe_checksummed_and_refuses_overwrite(tmp_path: Path) -> None:
    profile = load_profile(ROOT / "capacity-profile.json")
    profile["soak"]["duration_seconds"] = 0.1
    bundle = build_evidence(profile, "synthetic-commit")
    assert bundle["schema_version"] == EVIDENCE_SCHEMA
    assert bundle["guardrail_result"] == "PASS"
    output = tmp_path / "capacity.json"
    checksum = write_evidence(bundle, output, ROOT)
    assert len(checksum) == 64
    assert json.loads(output.read_text(encoding="utf-8"))["commit"] == "synthetic-commit"
    with pytest.raises(FileExistsError):
        write_evidence(bundle, output, ROOT)
    with pytest.raises(ValueError):
        write_evidence(bundle, ROOT / "forbidden.json", ROOT)


@pytest.mark.parametrize("operations,concurrency", [(0, 1), (1, 0), (2001, 1), (1, 17)])
def test_unbounded_load_is_rejected(operations: int, concurrency: int) -> None:
    with pytest.raises(ValueError):
        run_controlled_load(deterministic_operation, operations=operations, concurrency=concurrency)
