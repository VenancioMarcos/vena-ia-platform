import base64
import json
import shutil
from pathlib import Path

import pytest

from scripts.backup_contract import BackupContractError, BackupManifest, sha256_file
from scripts.backup_set import BackupSetManifest
from scripts.encrypted_backup import (
    ENCRYPTED_SET_CONTRACT_VERSION,
    EncryptionKey,
    create_encrypted_bundle,
    decrypt_bundle,
    load_encrypted_manifest,
)
from scripts.minio_backup import MinioBackupManifest, ObjectManifestEntry

SET_ID = "00000000-0000-4000-8000-000000000033"
CREATED_AT = "2026-08-02T18:00:00Z"
KEY = EncryptionKey("test-key-2026-08", bytes(range(32)))


def _plain_set(tmp_path: Path) -> tuple[Path, Path, Path]:
    postgres_root = tmp_path / "plain-postgres"
    postgres_root.mkdir(parents=True)
    dump = postgres_root / "database.dump"
    dump.write_bytes(b"PGDMP-encrypted-probe")
    postgres_manifest = postgres_root / "database.manifest.json"
    BackupManifest(
        contract_version="vena-ia.postgresql-backup/v1",
        backup_set_id=SET_ID,
        created_at=CREATED_AT,
        application_version="1.3.0-dev",
        database="vena_ia",
        database_server_version="17",
        migration_head="f42a1b7c9d30",
        format="postgresql-custom",
        backup_file=dump.name,
        size_bytes=dump.stat().st_size,
        sha256=sha256_file(dump),
    ).write(postgres_manifest)

    minio_root = tmp_path / "plain-minio"
    object_path = minio_root / "objects" / "projects" / "p" / "documents" / "d" / "file.pdf"
    object_path.parent.mkdir(parents=True)
    object_path.write_bytes(b"encrypted-minio-probe")
    minio_manifest = minio_root / "manifest.json"
    MinioBackupManifest(
        contract_version="vena-ia.minio-backup/v1",
        backup_set_id=SET_ID,
        created_at=CREATED_AT,
        application_version="1.3.0-dev",
        bucket="source",
        object_count=1,
        objects=[
            ObjectManifestEntry(
                object_key="projects/p/documents/d/file.pdf",
                size_bytes=object_path.stat().st_size,
                sha256=sha256_file(object_path),
                content_type="application/pdf",
                last_modified=CREATED_AT,
                etag=None,
                document_id="d",
                project_id="p",
                artifact_path="objects/projects/p/documents/d/file.pdf",
            )
        ],
    ).write(minio_manifest)

    combined_path = tmp_path / "backup-set.json"
    BackupSetManifest(
        contract_version="vena-ia.backup-set/v1",
        backup_set_id=SET_ID,
        created_at=CREATED_AT,
        application_version="1.3.0-dev",
        migration_head="f42a1b7c9d30",
        postgres_manifest=postgres_manifest.name,
        postgres_manifest_sha256=sha256_file(postgres_manifest),
        minio_manifest=minio_manifest.name,
        minio_manifest_sha256=sha256_file(minio_manifest),
        object_count=1,
        document_count=1,
        consistency_status="CONSISTENT",
    ).write(combined_path)
    return postgres_manifest, minio_manifest, combined_path


def _encrypted(tmp_path: Path, *, key: EncryptionKey = KEY, protected: bool = False):
    postgres, minio, combined = _plain_set(tmp_path / "source")
    return create_encrypted_bundle(
        tmp_path / "encrypted",
        postgres,
        minio,
        combined,
        key,
        retention_class="daily",
        protected=protected,
    )


def test_encrypted_bundle_contains_no_plaintext_and_round_trips(tmp_path: Path) -> None:
    root, index = _encrypted(tmp_path)
    manifest = load_encrypted_manifest(index, KEY)
    assert manifest.contract_version == ENCRYPTED_SET_CONTRACT_VERSION
    assert manifest.key_id == KEY.key_id
    assert manifest.retention_class == "daily"
    all_bytes = b"".join(path.read_bytes() for path in root.rglob("*.enc"))
    assert b"PGDMP-encrypted-probe" not in all_bytes
    assert b"encrypted-minio-probe" not in all_bytes
    assert KEY.value not in root.joinpath("encrypted-set.json").read_bytes()

    restored = decrypt_bundle(index, tmp_path / "restored", KEY)
    pg = BackupManifest.load(restored.postgres_manifest)
    minio = MinioBackupManifest.load(restored.minio_manifest)
    combined = BackupSetManifest.load(restored.backup_set_manifest)
    assert pg.backup_set_id == minio.backup_set_id == combined.backup_set_id == SET_ID
    assert (restored.postgres_manifest.parent / pg.backup_file).read_bytes().startswith(b"PGDMP")
    assert (restored.minio_manifest.parent / minio.objects[0].artifact_path).read_bytes() == b"encrypted-minio-probe"


def test_key_is_required_validated_and_never_defaulted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BACKUP_ENCRYPTION_KEY", raising=False)
    monkeypatch.delenv("BACKUP_ENCRYPTION_KEY_ID", raising=False)
    with pytest.raises(BackupContractError, match="required"):
        EncryptionKey.from_environment()
    monkeypatch.setenv("BACKUP_ENCRYPTION_KEY_ID", "key-id")
    monkeypatch.setenv("BACKUP_ENCRYPTION_KEY", "invalid")
    with pytest.raises(BackupContractError, match="format|32 bytes"):
        EncryptionKey.from_environment()
    monkeypatch.setenv("BACKUP_ENCRYPTION_KEY", base64.b64encode(b"short").decode())
    with pytest.raises(BackupContractError, match="32 bytes"):
        EncryptionKey.from_environment()


def test_wrong_key_and_wrong_key_id_fail_closed_without_plaintext(tmp_path: Path) -> None:
    _, index = _encrypted(tmp_path)
    target = tmp_path / "target"
    with pytest.raises(BackupContractError, match="key ID"):
        decrypt_bundle(index, target, EncryptionKey("wrong-id", KEY.value))
    assert not target.exists()
    with pytest.raises(BackupContractError, match="authentication"):
        decrypt_bundle(index, target, EncryptionKey(KEY.key_id, bytes(reversed(KEY.value))))
    assert not target.exists()
    assert not list(tmp_path.glob(".target.partial-*"))


@pytest.mark.parametrize("target", ["index", "manifest", "artifact"])
def test_tampering_and_partial_encryption_fail_closed(tmp_path: Path, target: str) -> None:
    root, index = _encrypted(tmp_path)
    if target == "index":
        payload = json.loads(index.read_text(encoding="utf-8"))
        payload["nonce_b64"] = base64.b64encode(b"0" * 12).decode()
        index.write_text(json.dumps(payload), encoding="utf-8")
    elif target == "manifest":
        (root / "manifest.enc").write_bytes(b"tampered")
    else:
        next((root / "artifacts").glob("*.enc")).unlink()
    with pytest.raises(BackupContractError, match="authentication|tampered|incomplete|corrupted"):
        load_encrypted_manifest(index, KEY)


def test_unknown_algorithm_unencrypted_input_and_overwrite_are_refused(tmp_path: Path) -> None:
    root, index = _encrypted(tmp_path)
    payload = json.loads(index.read_text(encoding="utf-8"))
    payload["encryption_algorithm"] = "unknown"
    index.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(BackupContractError, match="unsupported"):
        load_encrypted_manifest(index, KEY)
    with pytest.raises(BackupContractError, match="invalid"):
        load_encrypted_manifest(root / "manifest.enc", KEY)

    postgres, minio, combined = _plain_set(tmp_path / "second-source")
    with pytest.raises(BackupContractError, match="overwrite"):
        create_encrypted_bundle(
            tmp_path / "encrypted", postgres, minio, combined, KEY
        )


def test_manifest_disagreement_and_decrypt_destination_are_refused(tmp_path: Path) -> None:
    postgres, minio, combined = _plain_set(tmp_path / "source")
    payload = json.loads(combined.read_text(encoding="utf-8"))
    payload["minio_manifest_sha256"] = "0" * 64
    combined.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(BackupContractError, match="checksum"):
        create_encrypted_bundle(tmp_path / "encrypted", postgres, minio, combined, KEY)

    _, index = _encrypted(tmp_path / "valid")
    destination = tmp_path / "exists"
    destination.mkdir()
    with pytest.raises(BackupContractError, match="overwrite"):
        decrypt_bundle(index, destination, KEY)


def test_plaintext_sources_can_be_removed_after_encryption(tmp_path: Path) -> None:
    source = tmp_path / "source"
    postgres, minio, combined = _plain_set(source)
    _, index = create_encrypted_bundle(
        tmp_path / "encrypted", postgres, minio, combined, KEY
    )
    shutil.rmtree(source)
    restored = decrypt_bundle(index, tmp_path / "restored", KEY)
    assert restored.root.is_dir()
