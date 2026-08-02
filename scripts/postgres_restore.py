"""Verify and restore a PostgreSQL backup into an explicitly confirmed target."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.backup_contract import (
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


def restore_backup(
    manifest_path: Path,
    config: DatabaseConfig,
    *,
    confirmed_database: str,
    allowed_database: str,
    pg_restore_bin: str = "pg_restore",
    psql_bin: str = "psql",
    runner: Runner = run_postgres_command,
) -> None:
    safe_manifest_path = ensure_outside_repository(manifest_path)
    manifest = BackupManifest.load(safe_manifest_path)
    backup_path = safe_manifest_path.parent / manifest.backup_file
    ensure_outside_repository(backup_path)
    if confirmed_database != config.database or allowed_database != config.database:
        raise BackupContractError("Restore target was not explicitly confirmed and allowed")
    if not backup_path.is_file():
        raise BackupContractError("Backup file referenced by manifest is missing")
    if backup_path.stat().st_size != manifest.size_bytes:
        raise BackupContractError("Backup size does not match manifest")
    if sha256_file(backup_path) != manifest.sha256:
        raise BackupContractError("Backup checksum does not match manifest")

    table_count = query_scalar(
        config,
        "SELECT count(*) FROM pg_catalog.pg_tables "
        "WHERE schemaname NOT IN ('pg_catalog', 'information_schema');",
        psql_bin=psql_bin,
        runner=runner,
    )
    if table_count != "0":
        raise BackupContractError("Restore target is not empty; refusing overwrite")

    runner(
        [
            pg_restore_bin,
            *connection_arguments(config),
            "--exit-on-error",
            "--no-owner",
            "--no-privileges",
            str(backup_path),
        ],
        config.password,
        False,
    )
    restored_head = query_scalar(
        config,
        "SELECT version_num FROM alembic_version;",
        psql_bin=psql_bin,
        runner=runner,
    )
    if restored_head != manifest.migration_head:
        raise BackupContractError("Restored migration head does not match manifest")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--target-database", required=True)
    parser.add_argument("--confirm-target", required=True)
    parser.add_argument("--allow-database")
    parser.add_argument("--pg-restore-bin", default="pg_restore")
    parser.add_argument("--psql-bin", default="psql")
    args = parser.parse_args()
    allowed_database = args.allow_database or os.getenv("BACKUP_RESTORE_ALLOWED_DATABASE")
    if not allowed_database:
        parser.error("--allow-database or BACKUP_RESTORE_ALLOWED_DATABASE is required")
    try:
        restore_backup(
            args.manifest,
            DatabaseConfig.from_environment(database=args.target_database),
            confirmed_database=args.confirm_target,
            allowed_database=allowed_database,
            pg_restore_bin=args.pg_restore_bin,
            psql_bin=args.psql_bin,
        )
    except BackupContractError as exc:
        parser.error(str(exc))
    print(f"restored_database={args.target_database}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
