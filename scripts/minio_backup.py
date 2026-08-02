"""Versioned MinIO object backup and controlled restore primitives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Protocol
from uuid import UUID, uuid4

from minio import Minio
from minio.error import MinioException, S3Error

from scripts.backup_contract import BackupContractError, ensure_outside_repository, sha256_file

MINIO_CONTRACT_VERSION = "vena-ia.minio-backup/v1"


class ReadableResponse(Protocol):
    def read(self, amount: int | None = None) -> bytes: ...


@dataclass(frozen=True)
class ObjectManifestEntry:
    object_key: str
    size_bytes: int
    sha256: str
    content_type: str
    last_modified: str
    etag: str | None
    document_id: str | None
    project_id: str | None
    artifact_path: str


@dataclass(frozen=True)
class MinioBackupManifest:
    contract_version: str
    backup_set_id: str
    created_at: str
    application_version: str
    bucket: str
    object_count: int
    objects: list[ObjectManifestEntry]

    @classmethod
    def load(cls, path: Path) -> MinioBackupManifest:
        try:
            payload: Any = json.loads(path.read_text(encoding="utf-8"))
            entries = [ObjectManifestEntry(**item) for item in payload.pop("objects")]
            manifest = cls(objects=entries, **payload)
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise BackupContractError("MinIO backup manifest is invalid") from exc
        if manifest.contract_version != MINIO_CONTRACT_VERSION:
            raise BackupContractError("MinIO backup manifest contract is unsupported")
        try:
            UUID(manifest.backup_set_id)
            datetime.fromisoformat(manifest.created_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as exc:
            raise BackupContractError("MinIO backup identity or timestamp is invalid") from exc
        if not manifest.application_version or not manifest.bucket:
            raise BackupContractError("MinIO backup source metadata is invalid")
        if manifest.object_count != len(manifest.objects):
            raise BackupContractError("MinIO object count does not match manifest")
        keys = [entry.object_key for entry in manifest.objects]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise BackupContractError("MinIO manifest object keys are not deterministic")
        artifact_paths: list[str] = []
        for entry in manifest.objects:
            _safe_parts(entry.object_key)
            _safe_parts(entry.artifact_path)
            artifact_paths.append(entry.artifact_path)
            if not entry.artifact_path.startswith("objects/"):
                raise BackupContractError("MinIO artifact path is unsafe")
            if not re.fullmatch(r"[0-9a-f]{64}", entry.sha256) or entry.size_bytes < 0:
                raise BackupContractError("MinIO object metadata is invalid")
        if len(artifact_paths) != len(set(artifact_paths)):
            raise BackupContractError("MinIO manifest artifact paths are duplicated")
        return manifest

    def write(self, path: Path) -> None:
        path.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _safe_parts(value: str) -> tuple[str, ...]:
    if not value or "\\" in value or "\x00" in value:
        raise BackupContractError("MinIO object path is unsafe")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise BackupContractError("MinIO object path is unsafe")
    return path.parts


def _safe_artifact(root: Path, relative: str) -> Path:
    target = root.joinpath(*_safe_parts(relative))
    if target.exists() and target.is_symlink():
        raise BackupContractError("Symlink artifacts are forbidden")
    current = target.parent
    while current != root.parent:
        if current.exists() and current.is_symlink():
            raise BackupContractError("Symlink artifact parents are forbidden")
        if current == root:
            break
        current = current.parent
    resolved = target.resolve()
    if root.resolve() not in resolved.parents:
        raise BackupContractError("MinIO artifact escapes backup root")
    return target


def _identifiers(object_key: str) -> tuple[str | None, str | None]:
    parts = _safe_parts(object_key)
    if len(parts) >= 4 and parts[0] == "projects" and parts[2] == "documents":
        return parts[3], parts[1]
    return None, None


def _download_to_file(response: ReadableResponse, target: Path) -> str:
    digest = hashlib.sha256()
    size = 0
    with target.open("xb") as output:
        while block := response.read(1024 * 1024):
            output.write(block)
            digest.update(block)
            size += len(block)
    if target.stat().st_size != size:
        raise BackupContractError("MinIO artifact size verification failed")
    return digest.hexdigest()


def create_minio_backup(
    output_directory: Path,
    client: Minio,
    bucket: str,
    *,
    application_version: str,
    backup_set_id: str | None = None,
    now: datetime | None = None,
) -> tuple[Path, Path]:
    directory = ensure_outside_repository(output_directory)
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    set_id = backup_set_id or str(uuid4())
    try:
        UUID(set_id)
    except ValueError as exc:
        raise BackupContractError("MinIO backup-set identifier is invalid") from exc
    root = directory / f"vena-ia-minio-{timestamp.strftime('%Y%m%dT%H%M%SZ')}-{set_id}"
    if root.exists():
        raise BackupContractError("MinIO backup set already exists; refusing overwrite")
    objects_root = root / "objects"
    objects_root.mkdir(parents=True)
    entries: list[ObjectManifestEntry] = []
    try:
        for item in sorted(client.list_objects(bucket, recursive=True), key=lambda value: value.object_name):
            key = item.object_name
            parts = _safe_parts(key)
            artifact_relative = PurePosixPath("objects", *parts).as_posix()
            artifact = _safe_artifact(root, artifact_relative)
            artifact.parent.mkdir(parents=True, exist_ok=True)
            response = client.get_object(bucket, key)
            try:
                checksum = _download_to_file(response, artifact)
            finally:
                response.close()
                response.release_conn()
            stat = client.stat_object(bucket, key)
            if artifact.stat().st_size != stat.size:
                raise BackupContractError("MinIO object size changed during backup")
            document_id, project_id = _identifiers(key)
            etag = stat.etag if stat.etag and "-" not in stat.etag else None
            if stat.last_modified is None:
                raise BackupContractError("MinIO object timestamp is missing")
            last_modified = stat.last_modified.astimezone(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            entries.append(
                ObjectManifestEntry(
                    object_key=key,
                    size_bytes=stat.size,
                    sha256=checksum,
                    content_type=stat.content_type or "application/octet-stream",
                    last_modified=last_modified,
                    etag=etag,
                    document_id=document_id,
                    project_id=project_id,
                    artifact_path=artifact_relative,
                )
            )
    except (MinioException, S3Error, OSError) as exc:
        shutil.rmtree(root, ignore_errors=True)
        raise BackupContractError("MinIO backup failed") from exc
    except BackupContractError:
        shutil.rmtree(root, ignore_errors=True)
        raise
    manifest = MinioBackupManifest(
        contract_version=MINIO_CONTRACT_VERSION,
        backup_set_id=set_id,
        created_at=timestamp.isoformat().replace("+00:00", "Z"),
        application_version=application_version,
        bucket=bucket,
        object_count=len(entries),
        objects=entries,
    )
    manifest_path = root / "manifest.json"
    manifest.write(manifest_path)
    return root, manifest_path


def restore_minio_backup(
    manifest_path: Path,
    client: Minio,
    target_bucket: str,
    *,
    confirmed_bucket: str,
    allowed_bucket: str,
    target_prefix: str = "",
) -> None:
    safe_manifest = ensure_outside_repository(manifest_path)
    manifest = MinioBackupManifest.load(safe_manifest)
    root = safe_manifest.parent
    if confirmed_bucket != target_bucket or allowed_bucket != target_bucket:
        raise BackupContractError("MinIO restore target was not explicitly confirmed and allowed")
    prefix = target_prefix.strip("/")
    if target_prefix and prefix != target_prefix:
        raise BackupContractError("MinIO restore prefix is unsafe")
    if prefix:
        _safe_parts(prefix)
    artifacts: list[tuple[ObjectManifestEntry, Path]] = []
    for entry in manifest.objects:
        artifact = _safe_artifact(root, entry.artifact_path)
        if not artifact.is_file() or artifact.is_symlink():
            raise BackupContractError("MinIO backup artifact is missing or unsafe")
        if artifact.stat().st_size != entry.size_bytes or sha256_file(artifact) != entry.sha256:
            raise BackupContractError("MinIO backup artifact is corrupted")
        artifacts.append((entry, artifact))

    created_bucket = False
    uploaded: list[str] = []
    try:
        if not client.bucket_exists(target_bucket):
            client.make_bucket(target_bucket)
            created_bucket = True
        if any(client.list_objects(target_bucket, prefix=prefix, recursive=True)):
            raise BackupContractError("MinIO restore destination is not empty")
        for entry, artifact in artifacts:
            destination = f"{prefix}/{entry.object_key}" if prefix else entry.object_key
            with artifact.open("rb") as data:
                client.put_object(
                    target_bucket,
                    destination,
                    data,
                    length=entry.size_bytes,
                    content_type=entry.content_type,
                )
            uploaded.append(destination)
            stat = client.stat_object(target_bucket, destination)
            if stat.size != entry.size_bytes:
                raise BackupContractError("MinIO restore size verification failed")
            response = client.get_object(target_bucket, destination)
            try:
                digest = hashlib.sha256(response.read()).hexdigest()
            finally:
                response.close()
                response.release_conn()
            if digest != entry.sha256:
                raise BackupContractError("MinIO restore checksum verification failed")
    except (MinioException, S3Error, OSError) as exc:
        _cleanup_restore(client, target_bucket, uploaded, created_bucket)
        raise BackupContractError("MinIO restore failed") from exc
    except BackupContractError:
        _cleanup_restore(client, target_bucket, uploaded, created_bucket)
        raise


def _cleanup_restore(client: Minio, bucket: str, uploaded: list[str], remove_bucket: bool) -> None:
    try:
        for key in reversed(uploaded):
            client.remove_object(bucket, key)
        if remove_bucket:
            client.remove_bucket(bucket)
    except (MinioException, S3Error, OSError):
        raise BackupContractError("MinIO restore cleanup failed") from None


def client_from_environment() -> Minio:
    endpoint = os.getenv("MINIO_ENDPOINT", "")
    access_key = os.getenv("MINIO_ACCESS_KEY", "")
    secret_key = os.getenv("MINIO_SECRET_KEY", "")
    if not endpoint or not access_key or not secret_key:
        raise BackupContractError("MinIO endpoint and credentials are required")
    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--bucket")
    parser.add_argument("--application-version", default="1.3.0-dev")
    parser.add_argument("--backup-set-id")
    args = parser.parse_args()
    output = args.output_directory
    if output is None and os.getenv("BACKUP_OUTPUT_DIRECTORY"):
        output = Path(os.environ["BACKUP_OUTPUT_DIRECTORY"])
    bucket = args.bucket or os.getenv("MINIO_BUCKET")
    if output is None or not bucket:
        parser.error("backup output directory and MinIO bucket are required")
    try:
        root, manifest = create_minio_backup(
            output,
            client_from_environment(),
            bucket,
            application_version=args.application_version,
            backup_set_id=args.backup_set_id,
        )
    except BackupContractError as exc:
        parser.error(str(exc))
    print(f"backup={root}")
    print(f"manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
