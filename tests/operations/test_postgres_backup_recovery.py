import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.backup_contract import (
    REPOSITORY_ROOT,
    BackupContractError,
    DatabaseConfig,
)
from scripts.postgres_backup import create_backup
from scripts.postgres_restore import restore_backup

MIGRATION_HEAD = "f42a1b7c9d30"
PASSWORD = "test-only-database-password"


class FakePostgresRunner:
    def __init__(self, *, table_count: str = "0") -> None:
        self.commands: list[list[str]] = []
        self.table_count = table_count

    def __call__(self, command: list[str], password: str, capture: bool) -> str:
        assert password == PASSWORD
        assert password not in command
        self.commands.append(command)
        if command[0] == "psql":
            query = command[-1]
            if "alembic_version" in query:
                return MIGRATION_HEAD
            if "server_version" in query:
                return "17.6"
            if "pg_catalog.pg_tables" in query:
                return self.table_count
        if command[0] == "pg_dump":
            output = Path(command[command.index("--file") + 1])
            output.write_bytes(b"PGDMP-test-content")
        assert capture is (command[0] == "psql")
        return ""


@pytest.fixture()
def config() -> DatabaseConfig:
    return DatabaseConfig("localhost", 5432, "vena_ia", "vena_ia", PASSWORD)


def _create_set(tmp_path: Path, config: DatabaseConfig):
    runner = FakePostgresRunner()
    paths = create_backup(
        tmp_path,
        config,
        application_version="1.2.0",
        runner=runner,
        now=datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc),
    )
    return paths, runner


def test_backup_creates_versioned_manifest_checksum_and_no_secret(
    tmp_path: Path,
    config: DatabaseConfig,
) -> None:
    (backup, manifest_path), runner = _create_set(tmp_path, config)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert backup.name == "vena-ia-postgres-20260802T120000Z.dump"
    assert manifest["contract_version"] == "vena-ia.postgresql-backup/v1"
    assert manifest["application_version"] == "1.2.0"
    assert manifest["migration_head"] == MIGRATION_HEAD
    assert manifest["database_server_version"] == "17.6"
    assert manifest["backup_file"] == backup.name
    assert len(manifest["sha256"]) == 64
    assert PASSWORD not in manifest_path.read_text(encoding="utf-8")
    assert all(PASSWORD not in command for command in runner.commands)


def test_backup_refuses_repository_and_overwrite(
    tmp_path: Path,
    config: DatabaseConfig,
) -> None:
    with pytest.raises(BackupContractError, match="outside"):
        create_backup(
            REPOSITORY_ROOT / "unsafe-backup",
            config,
            application_version="1.2.0",
            runner=FakePostgresRunner(),
        )

    _create_set(tmp_path, config)
    with pytest.raises(BackupContractError, match="overwrite"):
        create_backup(
            tmp_path,
            config,
            application_version="1.2.0",
            runner=FakePostgresRunner(),
            now=datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc),
        )


def test_restore_verifies_target_checksum_and_migration(
    tmp_path: Path,
    config: DatabaseConfig,
) -> None:
    (_, manifest), _ = _create_set(tmp_path, config)
    runner = FakePostgresRunner()

    restore_backup(
        manifest,
        config,
        confirmed_database=config.database,
        allowed_database=config.database,
        runner=runner,
    )

    restore_command = next(command for command in runner.commands if command[0] == "pg_restore")
    assert "--exit-on-error" in restore_command
    assert "--no-owner" in restore_command
    assert "--clean" not in restore_command


@pytest.mark.parametrize(
    ("confirmed", "allowed"),
    [("wrong", "vena_ia"), ("vena_ia", "wrong")],
)
def test_restore_requires_exact_confirmation_and_allowlist(
    tmp_path: Path,
    config: DatabaseConfig,
    confirmed: str,
    allowed: str,
) -> None:
    (_, manifest), _ = _create_set(tmp_path, config)
    with pytest.raises(BackupContractError, match="explicitly confirmed"):
        restore_backup(
            manifest,
            config,
            confirmed_database=confirmed,
            allowed_database=allowed,
            runner=FakePostgresRunner(),
        )


def test_restore_refuses_tampered_backup_and_nonempty_database(
    tmp_path: Path,
    config: DatabaseConfig,
) -> None:
    (backup, manifest), _ = _create_set(tmp_path, config)
    backup.write_bytes(b"tampered")
    with pytest.raises(BackupContractError, match="size|checksum"):
        restore_backup(
            manifest,
            config,
            confirmed_database=config.database,
            allowed_database=config.database,
            runner=FakePostgresRunner(),
        )

    (backup, manifest), _ = _create_set(tmp_path / "second", config)
    assert backup.exists()
    with pytest.raises(BackupContractError, match="not empty"):
        restore_backup(
            manifest,
            config,
            confirmed_database=config.database,
            allowed_database=config.database,
            runner=FakePostgresRunner(table_count="1"),
        )


def test_invalid_manifest_and_environment_are_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    config: DatabaseConfig,
) -> None:
    bad_manifest = tmp_path / "bad.manifest.json"
    bad_manifest.write_text("{}", encoding="utf-8")
    with pytest.raises(BackupContractError, match="invalid"):
        restore_backup(
            bad_manifest,
            config,
            confirmed_database=config.database,
            allowed_database=config.database,
            runner=FakePostgresRunner(),
        )

    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    with pytest.raises(BackupContractError):
        DatabaseConfig.from_environment()
