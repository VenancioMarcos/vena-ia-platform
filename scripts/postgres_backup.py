"""Create a PostgreSQL custom-format backup and a verifiable manifest."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from scripts.backup_contract import (
    CONTRACT_VERSION,
    BackupContractError,
    BackupManifest,
    DatabaseConfig,
    Runner,
    connection_arguments,
    ensure_outside_repository,
    query_scalar,
    run_postgres_command,
    sha256_file,
)


def create_backup(
    output_directory: Path,
    config: DatabaseConfig,
    *,
    application_version: str,
    pg_dump_bin: str = "pg_dump",
    psql_bin: str = "psql",
    runner: Runner = run_postgres_command,
    now: datetime | None = None,
) -> tuple[Path, Path]:
    directory = ensure_outside_repository(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    backup_path = directory / f"vena-ia-postgres-{stamp}.dump"
    manifest_path = directory / f"vena-ia-postgres-{stamp}.manifest.json"
    if backup_path.exists() or manifest_path.exists():
        raise BackupContractError("Backup set already exists; refusing overwrite")

    migration_head = query_scalar(
        config,
        "SELECT version_num FROM alembic_version;",
        psql_bin=psql_bin,
        runner=runner,
    )
    server_version = query_scalar(
        config,
        "SHOW server_version;",
        psql_bin=psql_bin,
        runner=runner,
    )
    if not migration_head or not server_version:
        raise BackupContractError("Database schema metadata is unavailable")

    runner(
        [
            pg_dump_bin,
            *connection_arguments(config),
            "--format=custom",
            "--compress=6",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(backup_path),
        ],
        config.password,
        False,
    )
    if not backup_path.is_file() or backup_path.stat().st_size == 0:
        raise BackupContractError("pg_dump did not create a non-empty backup")

    manifest = BackupManifest(
        contract_version=CONTRACT_VERSION,
        backup_set_id=str(uuid4()),
        created_at=timestamp.isoformat().replace("+00:00", "Z"),
        application_version=application_version,
        database=config.database,
        database_server_version=server_version,
        migration_head=migration_head,
        format="postgresql-custom",
        backup_file=backup_path.name,
        size_bytes=backup_path.stat().st_size,
        sha256=sha256_file(backup_path),
    )
    manifest.write(manifest_path)
    return backup_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--application-version", default="1.2.0")
    parser.add_argument("--pg-dump-bin", default="pg_dump")
    parser.add_argument("--psql-bin", default="psql")
    args = parser.parse_args()
    output_directory = args.output_directory
    if output_directory is None and os.getenv("BACKUP_OUTPUT_DIRECTORY"):
        output_directory = Path(os.environ["BACKUP_OUTPUT_DIRECTORY"])
    if output_directory is None:
        parser.error("--output-directory or BACKUP_OUTPUT_DIRECTORY is required")
    try:
        backup, manifest = create_backup(
            output_directory,
            DatabaseConfig.from_environment(),
            application_version=args.application_version,
            pg_dump_bin=args.pg_dump_bin,
            psql_bin=args.psql_bin,
        )
    except BackupContractError as exc:
        parser.error(str(exc))
    print(f"backup={backup}")
    print(f"manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
