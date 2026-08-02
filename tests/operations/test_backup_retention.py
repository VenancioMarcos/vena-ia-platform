import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest

from scripts.backup_contract import REPOSITORY_ROOT, BackupContractError, sha256_file
from scripts.backup_retention import RetentionPolicy, execute_retention
from scripts.encrypted_backup import EncryptionKey, create_encrypted_bundle
from tests.operations.test_encrypted_backup import _plain_set

KEY = EncryptionKey("retention-test-key", bytes(range(32)))
NOW = datetime(2026, 8, 2, 20, 0, tzinfo=timezone.utc)


def _make_set(
    root: Path,
    sequence: int,
    created_at: datetime,
    *,
    retention_class: str = "daily",
    protected: bool = False,
) -> Path:
    set_id = str(UUID(int=sequence + 100))
    postgres, minio, combined = _plain_set(root / "sources" / str(sequence))
    timestamp = created_at.isoformat().replace("+00:00", "Z")
    postgres_payload = json.loads(postgres.read_text(encoding="utf-8"))
    postgres_payload.update(backup_set_id=set_id, created_at=timestamp)
    postgres.write_text(json.dumps(postgres_payload), encoding="utf-8")
    minio_payload = json.loads(minio.read_text(encoding="utf-8"))
    minio_payload.update(backup_set_id=set_id, created_at=timestamp)
    minio.write_text(json.dumps(minio_payload), encoding="utf-8")
    combined_payload = json.loads(combined.read_text(encoding="utf-8"))
    combined_payload.update(
        backup_set_id=set_id,
        created_at=timestamp,
        postgres_manifest_sha256=sha256_file(postgres),
        minio_manifest_sha256=sha256_file(minio),
    )
    combined.write_text(json.dumps(combined_payload), encoding="utf-8")
    _, index = create_encrypted_bundle(
        root / "sets",
        postgres,
        minio,
        combined,
        KEY,
        retention_class=retention_class,
        protected=protected,
    )
    return index.parent


def test_dry_run_is_default_and_apply_requires_exact_root(tmp_path: Path) -> None:
    sets = [_make_set(tmp_path, number, NOW - timedelta(days=number)) for number in range(3)]
    policy = RetentionPolicy(daily_keep=1, daily_max_age_days=30)
    report = execute_retention(tmp_path / "sets", KEY, policy, now=NOW)
    assert report.dry_run is True
    assert report.removed == 2
    assert all(path.exists() for path in sets)

    with pytest.raises(BackupContractError, match="confirmed"):
        execute_retention(
            tmp_path / "sets",
            KEY,
            policy,
            now=NOW,
            apply=True,
            confirmed_root=tmp_path / "wrong",
        )
    applied = execute_retention(
        tmp_path / "sets",
        KEY,
        policy,
        now=NOW,
        apply=True,
        confirmed_root=tmp_path / "sets",
    )
    assert applied.dry_run is False
    assert len(list((tmp_path / "sets").glob("vena-ia-encrypted-*"))) == 1


def test_age_quantity_classes_and_protected_sets(tmp_path: Path) -> None:
    recent = _make_set(tmp_path, 1, NOW, retention_class="daily")
    old_daily = _make_set(tmp_path, 2, NOW - timedelta(days=40), retention_class="daily")
    old_weekly = _make_set(tmp_path, 3, NOW - timedelta(days=90), retention_class="weekly")
    protected = _make_set(
        tmp_path,
        4,
        NOW - timedelta(days=900),
        retention_class="monthly",
        protected=True,
    )
    report = execute_retention(
        tmp_path / "sets",
        KEY,
        RetentionPolicy(
            daily_keep=5,
            weekly_keep=5,
            monthly_keep=5,
            daily_max_age_days=14,
            weekly_max_age_days=60,
            monthly_max_age_days=400,
        ),
        now=NOW,
    )
    decisions = {decision.backup_set: decision for decision in report.decisions}
    assert decisions[recent.name].action == "maintain"
    assert decisions[old_daily.name].reason == "age"
    assert decisions[old_weekly.name].reason == "age"
    assert decisions[protected.name].reason == "protected"


def test_incomplete_or_tampered_set_refuses_all_deletion(tmp_path: Path) -> None:
    valid = _make_set(tmp_path, 1, NOW - timedelta(days=30))
    incomplete = tmp_path / "sets" / "vena-ia-encrypted-incomplete"
    incomplete.mkdir()
    with pytest.raises(BackupContractError, match="invalid|incomplete"):
        execute_retention(
            tmp_path / "sets",
            KEY,
            RetentionPolicy(daily_keep=1, daily_max_age_days=1),
            now=NOW,
            apply=True,
            confirmed_root=tmp_path / "sets",
        )
    assert valid.exists()


def test_last_valid_set_is_never_removed(tmp_path: Path) -> None:
    only = _make_set(tmp_path, 1, NOW - timedelta(days=999))
    report = execute_retention(
        tmp_path / "sets",
        KEY,
        RetentionPolicy(daily_keep=1, daily_max_age_days=1),
        now=NOW,
        apply=True,
        confirmed_root=tmp_path / "sets",
    )
    assert report.removed == 0
    assert only.exists()
    assert report.decisions[0].reason == "last-valid-set"


def test_invalid_policy_repository_root_and_symlink_are_refused(tmp_path: Path) -> None:
    with pytest.raises(BackupContractError, match="positive"):
        RetentionPolicy(daily_keep=0).validate()
    with pytest.raises(BackupContractError, match="outside"):
        execute_retention(REPOSITORY_ROOT, KEY, RetentionPolicy())

    sets_root = tmp_path / "sets"
    sets_root.mkdir()
    real = tmp_path / "real"
    real.mkdir()
    link = sets_root / "vena-ia-encrypted-link"
    try:
        link.symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks require an OS privilege unavailable to this test process")
    with pytest.raises(BackupContractError, match="unsafe"):
        execute_retention(sets_root, KEY, RetentionPolicy())
