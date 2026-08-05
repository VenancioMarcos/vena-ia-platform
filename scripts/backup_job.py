"""Run one encrypted cross-store backup under a lock and bounded timeout."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import Any
from uuid import uuid4

from psycopg import connect

from scripts.backup_contract import BackupContractError, DatabaseConfig, ensure_outside_repository
from scripts.backup_set import DocumentReference, create_backup_set_manifest
from scripts.encrypted_backup import EncryptionKey, create_encrypted_bundle
from scripts.minio_backup import client_from_environment, create_minio_backup
from scripts.postgres_backup import create_backup


class ExclusiveBackupLock(AbstractContextManager["ExclusiveBackupLock"]):
    def __init__(self, path: Path) -> None:
        self.path = ensure_outside_repository(path)
        self.acquired = False

    def __enter__(self) -> ExclusiveBackupLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("x", encoding="utf-8") as lock_file:
                lock_file.write("vena-ia-backup-job\n")
            try:
                self.path.chmod(0o600)
            except OSError:
                pass
        except FileExistsError as exc:
            raise BackupContractError("Another backup job already holds the lock") from exc
        self.acquired = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback
        if self.acquired:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            self.acquired = False


def run_scheduled_worker(
    lock_path: Path,
    timeout_seconds: int,
    *,
    runner: Any = subprocess.run,
) -> None:
    if timeout_seconds < 1:
        raise BackupContractError("Backup job timeout must be positive")
    with ExclusiveBackupLock(lock_path):
        try:
            runner(
                [sys.executable, "-m", "scripts.backup_job", "--worker"],
                check=True,
                timeout=timeout_seconds,
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired as exc:
            raise BackupContractError("Backup job exceeded its configured timeout") from exc
        except (OSError, subprocess.CalledProcessError) as exc:
            raise BackupContractError("Backup job worker failed") from exc


def _document_references(config: DatabaseConfig) -> list[DocumentReference]:
    try:
        with connect(
            host=config.host,
            port=config.port,
            dbname=config.database,
            user=config.user,
            password=config.password,
        ) as connection:
            rows = connection.execute(
                "SELECT id::text, project_id::text, storage_path FROM documents ORDER BY storage_path"
            ).fetchall()
    except Exception as exc:
        raise BackupContractError("Document metadata could not be read for backup consistency") from exc
    return [DocumentReference(row[0], row[1], row[2]) for row in rows]


def create_encrypted_cross_store_backup() -> tuple[Path, float]:
    if os.getenv("BACKUP_CONSISTENCY_GUARD") != "quiesced":
        raise BackupContractError("Backup requires an explicitly quiesced consistency window")
    output_value = os.getenv("BACKUP_OUTPUT_DIRECTORY", "")
    bucket = os.getenv("MINIO_BUCKET", "")
    if not output_value or not bucket:
        raise BackupContractError("Backup output directory and MinIO bucket are required")
    output = ensure_outside_repository(Path(output_value))
    output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    now = started.replace(microsecond=0)
    backup_set_id = str(uuid4())
    config = DatabaseConfig.from_environment()
    key = EncryptionKey.from_environment()
    application_version = os.getenv("BACKUP_APPLICATION_VERSION", "1.4.0-dev")
    retention_class = os.getenv("BACKUP_RETENTION_CLASS", "daily")
    protected = os.getenv("BACKUP_SET_PROTECTED", "false").lower() == "true"
    with tempfile.TemporaryDirectory(prefix=".vena-ia-plaintext-", dir=output) as temporary:
        staging = Path(temporary)
        _, postgres_manifest = create_backup(
            staging / "postgres",
            config,
            application_version=application_version,
            backup_set_id=backup_set_id,
            now=now,
        )
        _, minio_manifest = create_minio_backup(
            staging / "minio",
            client_from_environment(),
            bucket,
            application_version=application_version,
            backup_set_id=backup_set_id,
            now=now,
        )
        backup_set_manifest = staging / f"vena-ia-backup-set-{backup_set_id}.json"
        create_backup_set_manifest(
            backup_set_manifest,
            postgres_manifest,
            minio_manifest,
            _document_references(config),
        )
        root, _ = create_encrypted_bundle(
            output,
            postgres_manifest,
            minio_manifest,
            backup_set_manifest,
            key,
            retention_class=retention_class,
            protected=protected,
        )
    duration = (datetime.now(timezone.utc) - started).total_seconds()
    return root, duration


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--timeout-seconds", type=int)
    args = parser.parse_args()
    try:
        if args.worker:
            root, duration = create_encrypted_cross_store_backup()
            print(f"backup_set={root.name}")
            print(f"backup_duration_seconds={duration:.3f}")
            return 0
        output_value = os.getenv("BACKUP_OUTPUT_DIRECTORY", "")
        if not output_value:
            raise BackupContractError("BACKUP_OUTPUT_DIRECTORY is required")
        output = ensure_outside_repository(Path(output_value))
        timeout = args.timeout_seconds or int(os.getenv("BACKUP_JOB_TIMEOUT_SECONDS", "3600"))
        run_scheduled_worker(output / ".backup-job.lock", timeout)
    except (BackupContractError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
