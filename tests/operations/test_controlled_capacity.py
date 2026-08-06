import json
import os
import threading
from pathlib import Path

import pytest

from scripts.capacity_process_gate import Gate
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


def test_capacity_bundle_creation_is_atomic_under_concurrency(tmp_path: Path) -> None:
    output = tmp_path / "capacity.json"
    outcomes: list[str] = []

    def write() -> None:
        try:
            write_evidence({"safe": True}, output, ROOT)
            outcomes.append("created")
        except FileExistsError:
            outcomes.append("refused")

    threads = [threading.Thread(target=write) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(outcomes) == ["created", "refused"]
    assert json.loads(output.read_text(encoding="utf-8")) == {"safe": True}
    assert not list(tmp_path.glob("*.tmp"))


def test_capacity_bundle_rejects_symlink_file_and_parent(tmp_path: Path) -> None:
    if not hasattr(os, "symlink"):
        pytest.skip("symlink is unavailable")
    target = tmp_path / "target"
    target.mkdir()
    linked_parent = tmp_path / "linked"
    try:
        linked_parent.symlink_to(target, target_is_directory=True)
        linked_file = tmp_path / "linked.json"
        linked_file.symlink_to(target / "payload.json")
    except OSError:
        pytest.skip("symlink creation is not permitted")
    with pytest.raises(ValueError):
        write_evidence({"safe": True}, linked_parent / "payload.json", ROOT)
    with pytest.raises(FileExistsError):
        write_evidence({"safe": True}, linked_file, ROOT)


def test_capacity_bundle_cleans_temporary_after_publish_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "capacity.json"

    def fail_link(*_args: object, **_kwargs: object) -> None:
        raise OSError("synthetic publish failure")

    monkeypatch.setattr(os, "link", fail_link)
    with pytest.raises(OSError, match="synthetic publish failure"):
        write_evidence({"safe": True}, output, ROOT)
    assert not os.path.lexists(output)
    assert list(tmp_path.iterdir()) == []


def test_failure_diagnostics_allowlist_only_exception_types(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    gate = object.__new__(Gate)
    worker_log = (tmp_path / "worker.log").open("w+b")
    worker_log.write(
        b"ERROR vena_ia.worker worker pre-claim dependency check failed: OperationalError\n"
        b"untrusted token=secret job_id=domain-id\n"
    )
    gate.logs = {"worker-a": worker_log}

    gate.emit_safe_diagnostics()

    assert capsys.readouterr().out == (
        "SAFE_WORKER_DIAGNOSTIC name=worker-a error_type=OperationalError\n"
    )
    worker_log.close()


@pytest.mark.parametrize("operations,concurrency", [(0, 1), (1, 0), (2001, 1), (1, 17)])
def test_unbounded_load_is_rejected(operations: int, concurrency: int) -> None:
    with pytest.raises(ValueError):
        run_controlled_load(deterministic_operation, operations=operations, concurrency=concurrency)
