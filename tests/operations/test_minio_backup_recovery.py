import io
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from scripts.backup_contract import BackupContractError, BackupManifest, sha256_file
from scripts.backup_set import (
    BACKUP_SET_CONTRACT_VERSION,
    DocumentReference,
    create_backup_set_manifest,
    validate_cross_store_consistency,
)
from scripts.minio_backup import (
    MINIO_CONTRACT_VERSION,
    MinioBackupManifest,
    create_minio_backup,
    client_from_environment,
    restore_minio_backup,
)

NOW = datetime(2026, 8, 2, 15, 30, tzinfo=timezone.utc)
SET_ID = "00000000-0000-4000-8000-000000000013"


class Response(io.BytesIO):
    def close(self) -> None:
        pass

    def release_conn(self) -> None:
        pass


class FakeMinio:
    def __init__(self, buckets: dict[str, dict[str, bytes]] | None = None) -> None:
        self.buckets = buckets or {}
        self.fail_put = False

    def list_objects(self, bucket: str, prefix: str = "", recursive: bool = True):
        del recursive
        if bucket not in self.buckets:
            raise RuntimeError("unavailable")
        return [
            SimpleNamespace(object_name=key)
            for key in self.buckets[bucket]
            if key.startswith(prefix)
        ]

    def get_object(self, bucket: str, key: str) -> Response:
        return Response(self.buckets[bucket][key])

    def stat_object(self, bucket: str, key: str):
        content = self.buckets[bucket][key]
        return SimpleNamespace(
            size=len(content),
            etag="a" * 32,
            content_type="application/pdf",
            last_modified=NOW,
        )

    def bucket_exists(self, bucket: str) -> bool:
        return bucket in self.buckets

    def make_bucket(self, bucket: str) -> None:
        self.buckets[bucket] = {}

    def put_object(
        self,
        bucket: str,
        key: str,
        data: Any,
        *,
        length: int,
        content_type: str,
    ) -> None:
        del content_type
        if self.fail_put:
            raise BackupContractError("injected write failure")
        value = data.read()
        assert len(value) == length
        self.buckets[bucket][key] = value

    def remove_object(self, bucket: str, key: str) -> None:
        self.buckets[bucket].pop(key)

    def remove_bucket(self, bucket: str) -> None:
        assert not self.buckets[bucket]
        self.buckets.pop(bucket)


def _client(value: FakeMinio) -> Any:
    return cast(Any, value)


def _backup(tmp_path: Path, objects: dict[str, bytes] | None = None):
    source = FakeMinio({"source": objects or {}})
    root, manifest = create_minio_backup(
        tmp_path,
        _client(source),
        "source",
        application_version="1.3.0-dev",
        backup_set_id=SET_ID,
        now=NOW,
    )
    return source, root, manifest


def test_empty_and_multiple_object_backups_are_deterministic(tmp_path: Path) -> None:
    _, _, empty_path = _backup(tmp_path / "empty")
    empty = MinioBackupManifest.load(empty_path)
    assert empty.contract_version == MINIO_CONTRACT_VERSION
    assert empty.object_count == 0

    objects = {
        "projects/project-b/documents/document-b/b.pdf": b"second",
        "projects/project-a/documents/document-a/a.pdf": b"first",
    }
    _, root, manifest_path = _backup(tmp_path / "multiple", objects)
    manifest = MinioBackupManifest.load(manifest_path)
    assert [entry.object_key for entry in manifest.objects] == sorted(objects)
    assert manifest.objects[0].project_id == "project-a"
    assert manifest.objects[0].document_id == "document-a"
    assert all((root / entry.artifact_path).read_bytes() == objects[entry.object_key] for entry in manifest.objects)
    assert "first" not in manifest_path.read_text(encoding="utf-8")

    with pytest.raises(BackupContractError, match="overwrite"):
        create_minio_backup(
            tmp_path / "multiple",
            _client(FakeMinio({"source": objects})),
            "source",
            application_version="1.3.0-dev",
            backup_set_id=SET_ID,
            now=NOW,
        )


def test_backup_reports_unavailable_storage_and_cleans_output(tmp_path: Path) -> None:
    client = FakeMinio({"source": {}})
    client.list_objects = cast(Any, lambda *args, **kwargs: (_ for _ in ()).throw(OSError("down")))
    with pytest.raises(BackupContractError, match="failed"):
        create_minio_backup(
            tmp_path,
            _client(client),
            "source",
            application_version="1.3.0-dev",
            backup_set_id=SET_ID,
            now=NOW,
        )
    assert not list(tmp_path.glob("vena-ia-minio-*"))


@pytest.mark.parametrize(
    "key",
    ["../escape", "/absolute", "projects/one/../escape", r"windows\escape"],
)
def test_backup_rejects_unsafe_object_paths_and_cleans_partial_output(
    tmp_path: Path, key: str
) -> None:
    with pytest.raises(BackupContractError, match="unsafe"):
        _backup(tmp_path, {key: b"bad"})
    assert not list(tmp_path.glob("vena-ia-minio-*"))


def test_restore_validates_every_artifact_before_mutation(tmp_path: Path) -> None:
    _, root, manifest_path = _backup(
        tmp_path / "backup", {"projects/p/documents/d/file.pdf": b"content"}
    )
    target = FakeMinio()
    artifact = next((root / "objects").rglob("*.pdf"))
    artifact.write_bytes(b"CONTENT")
    with pytest.raises(BackupContractError, match="corrupted"):
        restore_minio_backup(
            manifest_path,
            _client(target),
            "restore",
            confirmed_bucket="restore",
            allowed_bucket="restore",
        )
    assert "restore" not in target.buckets


def test_restore_requires_confirmation_allowlist_and_empty_destination(tmp_path: Path) -> None:
    _, _, manifest = _backup(tmp_path / "backup", {"safe/file": b"content"})
    with pytest.raises(BackupContractError, match="confirmed"):
        restore_minio_backup(
            manifest, _client(FakeMinio()), "restore", confirmed_bucket="wrong", allowed_bucket="restore"
        )
    with pytest.raises(BackupContractError, match="not empty"):
        restore_minio_backup(
            manifest,
            _client(FakeMinio({"restore": {"existing": b"data"}})),
            "restore",
            confirmed_bucket="restore",
            allowed_bucket="restore",
        )
    with pytest.raises(BackupContractError, match="unsafe"):
        restore_minio_backup(
            manifest,
            _client(FakeMinio()),
            "restore",
            confirmed_bucket="restore",
            allowed_bucket="restore",
            target_prefix="..",
        )


def test_minio_client_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(BackupContractError, match="credentials"):
        client_from_environment()


def test_restore_rejects_invalid_manifest_version_size_checksum_and_symlink(
    tmp_path: Path,
) -> None:
    _, root, manifest_path = _backup(tmp_path / "backup", {"safe/file": b"content"})
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    for field, value, expected in [
        ("contract_version", "unknown", "unsupported"),
        ("object_count", 2, "count"),
    ]:
        changed = dict(original)
        changed[field] = value
        manifest_path.write_text(json.dumps(changed), encoding="utf-8")
        with pytest.raises(BackupContractError, match=expected):
            MinioBackupManifest.load(manifest_path)
    original["objects"][0]["sha256"] = "z" * 64
    manifest_path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(BackupContractError, match="metadata"):
        MinioBackupManifest.load(manifest_path)

    link = root / "objects" / "link"
    try:
        link.symlink_to(root / "manifest.json")
    except OSError:
        pytest.skip("symlinks require an OS privilege unavailable to this test process")
    original["objects"][0]["sha256"] = sha256_file(root / "manifest.json")
    original["objects"][0]["size_bytes"] = (root / "manifest.json").stat().st_size
    original["objects"][0]["artifact_path"] = "objects/link"
    manifest_path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(BackupContractError, match="(?i)symlink"):
        restore_minio_backup(
            manifest_path,
            _client(FakeMinio()),
            "restore",
            confirmed_bucket="restore",
            allowed_bucket="restore",
        )


def test_restore_rolls_back_created_bucket_after_failure(tmp_path: Path) -> None:
    _, _, manifest = _backup(tmp_path / "backup", {"safe/file": b"content"})
    target = FakeMinio()
    target.fail_put = True
    with pytest.raises(BackupContractError):
        restore_minio_backup(
            manifest,
            _client(target),
            "restore",
            confirmed_bucket="restore",
            allowed_bucket="restore",
        )
    assert "restore" not in target.buckets


def _postgres_manifest(path: Path) -> Path:
    dump = path / "database.dump"
    dump.write_bytes(b"PGDMP")
    manifest_path = path / "postgres.json"
    BackupManifest(
        contract_version="vena-ia.postgresql-backup/v1",
        backup_set_id=SET_ID,
        created_at="2026-08-02T15:30:00Z",
        application_version="1.3.0-dev",
        database="vena_ia",
        database_server_version="17",
        migration_head="f42a1b7c9d30",
        format="custom",
        backup_file=dump.name,
        size_bytes=dump.stat().st_size,
        sha256=sha256_file(dump),
    ).write(manifest_path)
    return manifest_path


def test_backup_set_accepts_consistent_pair_and_refuses_overwrite(tmp_path: Path) -> None:
    key = "projects/project-a/documents/document-a/file.pdf"
    _, _, minio_path = _backup(tmp_path / "minio", {key: b"content"})
    postgres_path = _postgres_manifest(tmp_path)
    output = tmp_path / "backup-set.json"
    result = create_backup_set_manifest(
        output,
        postgres_path,
        minio_path,
        [DocumentReference("document-a", "project-a", key)],
    )
    assert result.contract_version == BACKUP_SET_CONTRACT_VERSION
    assert result.consistency_status == "CONSISTENT"
    with pytest.raises(BackupContractError, match="overwrite"):
        create_backup_set_manifest(output, postgres_path, minio_path, [])


@pytest.mark.parametrize("mode", ["missing", "orphan", "project-isolation", "document-isolation"])
def test_cross_store_consistency_fails_closed(tmp_path: Path, mode: str) -> None:
    key = "projects/project-a/documents/document-a/file.pdf"
    _, _, manifest_path = _backup(tmp_path, {key: b"content"})
    manifest = MinioBackupManifest.load(manifest_path)
    documents = [DocumentReference("document-a", "project-a", key)]
    if mode == "missing":
        documents.append(DocumentReference("document-b", "project-a", "missing"))
    elif mode == "orphan":
        documents = []
    elif mode == "project-isolation":
        documents = [replace(documents[0], project_id="project-b")]
    else:
        documents = [replace(documents[0], document_id="document-b")]
    with pytest.raises(BackupContractError, match="inconsistency|isolation"):
        validate_cross_store_consistency(documents, manifest)
