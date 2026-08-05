import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.backup_contract import REPOSITORY_ROOT
from scripts.incident_drill import (
    DRILL_SCHEMA_VERSION,
    IncidentDrillError,
    deterministic_json,
    run_controlled_drill,
    validate_report,
    verify_evidence_bundle,
    write_evidence_bundle,
)

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def test_controlled_drill_covers_required_correlated_signals_and_recovery() -> None:
    report = run_controlled_drill(now=NOW)
    assert report.schema_version == DRILL_SCHEMA_VERSION
    assert len(report.scenarios) == 11
    assert all(item.result == "pass" for item in report.scenarios)
    assert {item.dependency for item in report.scenarios} >= {"postgresql", "redis", "minio"}
    assert all(item.request_id and item.correlation_id for item in report.scenarios)
    assert all(item.alert_code and item.metric_name for item in report.scenarios)
    assert any(item.audit_event_type == "RATE_LIMIT_EXCEEDED" for item in report.scenarios)
    assert all(
        item.observed_state == "unavailable_then_ready"
        for item in report.scenarios
        if item.dependency is not None
    )


def test_report_is_deterministic_allowlisted_and_contains_no_sensitive_data() -> None:
    report = run_controlled_drill(now=NOW)
    first = deterministic_json(report)
    second = deterministic_json(report)
    assert first == second
    serialized = first.decode().lower()
    for prohibited in (
        "authorization",
        "cookie",
        "password",
        "secret",
        "user_id",
        "project_id",
        "document_id",
        "prompt",
        "embedding",
        "stack trace",
    ):
        assert prohibited not in serialized


def test_evidence_bundle_has_checksum_refuses_overwrite_and_repository(tmp_path: Path) -> None:
    report = run_controlled_drill(now=NOW)
    bundle = write_evidence_bundle(report, tmp_path)
    payload = bundle.report.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == bundle.sha256
    assert bundle.checksum.read_text(encoding="ascii") == (
        f"{bundle.sha256}  {bundle.report.name}\n"
    )
    assert verify_evidence_bundle(bundle.report, bundle.checksum) == report
    with pytest.raises(IncidentDrillError, match="overwrite"):
        write_evidence_bundle(report, tmp_path)
    with pytest.raises(IncidentDrillError, match="outside"):
        write_evidence_bundle(report, REPOSITORY_ROOT / "incident-evidence")


def test_bundle_verification_fails_closed_after_tampering(tmp_path: Path) -> None:
    bundle = write_evidence_bundle(run_controlled_drill(now=NOW), tmp_path)
    bundle.report.write_bytes(bundle.report.read_bytes() + b" ")
    with pytest.raises(IncidentDrillError, match="checksum"):
        verify_evidence_bundle(bundle.report, bundle.checksum)


def test_bundle_rejects_path_traversal_symlink_and_failed_report(tmp_path: Path) -> None:
    report = run_controlled_drill(now=NOW)
    with pytest.raises(IncidentDrillError, match="name is unsafe"):
        write_evidence_bundle(report, tmp_path, bundle_name="../escape")
    failed = replace(report, scenarios=(replace(report.scenarios[0], result="fail"), *report.scenarios[1:]))
    with pytest.raises(IncidentDrillError, match="failed"):
        validate_report(failed)
    link = tmp_path / "link"
    target = tmp_path / "target"
    target.mkdir()
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(IncidentDrillError, match="Symlinks"):
        write_evidence_bundle(report, link)


def test_contract_rejects_sensitive_limitations_and_invalid_thresholds() -> None:
    report = run_controlled_drill(now=NOW)
    unsafe = replace(
        report,
        scenarios=(
            replace(report.scenarios[0], limitations="authorization token exposed"),
            *report.scenarios[1:],
        ),
    )
    with pytest.raises(IncidentDrillError, match="allowlist"):
        validate_report(unsafe)
    payload = json.loads(deterministic_json(report))
    assert set(payload) == {
        "schema_version",
        "application_version",
        "environment",
        "started_at",
        "completed_at",
        "duration_ms",
        "scenarios",
    }
