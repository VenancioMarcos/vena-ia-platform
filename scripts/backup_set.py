"""Cross-store backup-set manifest and PostgreSQL/MinIO consistency checks."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from scripts.backup_contract import (
    BackupContractError,
    BackupManifest,
    ensure_outside_repository,
    sha256_file,
)
from scripts.minio_backup import MinioBackupManifest

BACKUP_SET_CONTRACT_VERSION = "vena-ia.backup-set/v1"


@dataclass(frozen=True)
class DocumentReference:
    document_id: str
    project_id: str
    object_key: str


@dataclass(frozen=True)
class BackupSetManifest:
    contract_version: str
    backup_set_id: str
    created_at: str
    application_version: str
    migration_head: str
    postgres_manifest: str
    postgres_manifest_sha256: str
    minio_manifest: str
    minio_manifest_sha256: str
    object_count: int
    document_count: int
    consistency_status: str

    @classmethod
    def load(cls, path: Path) -> BackupSetManifest:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            manifest = cls(**payload)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            raise BackupContractError("Backup-set manifest is invalid") from exc
        if manifest.contract_version != BACKUP_SET_CONTRACT_VERSION:
            raise BackupContractError("Backup-set manifest contract is unsupported")
        if manifest.consistency_status != "CONSISTENT":
            raise BackupContractError("Backup-set manifest is not consistent")
        if (
            not re.fullmatch(r"[0-9a-f]{64}", manifest.postgres_manifest_sha256)
            or not re.fullmatch(r"[0-9a-f]{64}", manifest.minio_manifest_sha256)
            or manifest.object_count < 0
            or manifest.document_count < 0
        ):
            raise BackupContractError("Backup-set manifest metadata is invalid")
        return manifest

    def write(self, path: Path) -> None:
        path.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def validate_cross_store_consistency(
    documents: list[DocumentReference],
    minio_manifest: MinioBackupManifest,
) -> None:
    expected = {document.object_key: document for document in documents}
    actual = {entry.object_key: entry for entry in minio_manifest.objects}
    if set(expected) != set(actual):
        missing = sorted(set(expected) - set(actual))
        orphaned = sorted(set(actual) - set(expected))
        raise BackupContractError(
            f"Cross-store inconsistency: missing={len(missing)}, orphaned={len(orphaned)}"
        )
    for key, document in expected.items():
        entry = actual[key]
        if entry.document_id != document.document_id or entry.project_id != document.project_id:
            raise BackupContractError("Cross-store project or document isolation mismatch")


def create_backup_set_manifest(
    output_path: Path,
    postgres_manifest_path: Path,
    minio_manifest_path: Path,
    documents: list[DocumentReference],
) -> BackupSetManifest:
    output_path = ensure_outside_repository(output_path)
    postgres_manifest_path = ensure_outside_repository(postgres_manifest_path)
    minio_manifest_path = ensure_outside_repository(minio_manifest_path)
    if output_path.exists():
        raise BackupContractError("Backup-set manifest exists; refusing overwrite")
    postgres = BackupManifest.load(postgres_manifest_path)
    minio = MinioBackupManifest.load(minio_manifest_path)
    if postgres.backup_set_id != minio.backup_set_id or postgres.created_at != minio.created_at:
        raise BackupContractError("Backup manifests do not belong to the same backup set")
    if postgres.application_version != minio.application_version:
        raise BackupContractError("Backup manifests use different application versions")
    validate_cross_store_consistency(documents, minio)
    manifest = BackupSetManifest(
        contract_version=BACKUP_SET_CONTRACT_VERSION,
        backup_set_id=postgres.backup_set_id,
        created_at=postgres.created_at,
        application_version=postgres.application_version,
        migration_head=postgres.migration_head,
        postgres_manifest=postgres_manifest_path.name,
        postgres_manifest_sha256=sha256_file(postgres_manifest_path),
        minio_manifest=minio_manifest_path.name,
        minio_manifest_sha256=sha256_file(minio_manifest_path),
        object_count=minio.object_count,
        document_count=len(documents),
        consistency_status="CONSISTENT",
    )
    manifest.write(output_path)
    return manifest
