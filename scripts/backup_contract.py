"""Versioned PostgreSQL backup contract shared by backup and restore CLIs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "vena-ia.postgresql-backup/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,62}$")


class BackupContractError(Exception):
    """A backup or restore safety condition was not satisfied."""


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_environment(cls, *, database: str | None = None) -> DatabaseConfig:
        selected_database = database or os.getenv("POSTGRES_DB", "") or ""
        user = os.getenv("POSTGRES_USER", "")
        password = os.getenv("POSTGRES_PASSWORD", "")
        host = os.getenv("POSTGRES_HOST", "localhost")
        try:
            port = int(os.getenv("POSTGRES_PORT", "5432"))
        except ValueError as exc:
            raise BackupContractError("POSTGRES_PORT must be an integer") from exc
        if not _IDENTIFIER.fullmatch(selected_database):
            raise BackupContractError("POSTGRES_DB is missing or invalid")
        if not _IDENTIFIER.fullmatch(user):
            raise BackupContractError("POSTGRES_USER is missing or invalid")
        if not password:
            raise BackupContractError("POSTGRES_PASSWORD must be supplied securely")
        if not host or not 1 <= port <= 65_535:
            raise BackupContractError("PostgreSQL host or port is invalid")
        return cls(host, port, selected_database, user, password)


@dataclass(frozen=True)
class BackupManifest:
    contract_version: str
    backup_set_id: str
    created_at: str
    application_version: str
    database: str
    database_server_version: str
    migration_head: str
    format: str
    backup_file: str
    size_bytes: int
    sha256: str

    @classmethod
    def load(cls, path: Path) -> BackupManifest:
        try:
            payload: Any = json.loads(path.read_text(encoding="utf-8"))
            manifest = cls(**payload)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            raise BackupContractError("Backup manifest is invalid") from exc
        if manifest.contract_version != CONTRACT_VERSION:
            raise BackupContractError("Backup manifest contract is unsupported")
        if not re.fullmatch(r"[0-9a-f]{64}", manifest.sha256):
            raise BackupContractError("Backup manifest checksum is invalid")
        if Path(manifest.backup_file).name != manifest.backup_file:
            raise BackupContractError("Backup manifest file name is unsafe")
        return manifest

    def write(self, path: Path) -> None:
        path.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


Runner = Callable[[list[str], str, bool], str]


def run_postgres_command(command: list[str], password: str, capture: bool) -> str:
    environment = os.environ.copy()
    environment["PGPASSWORD"] = password
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=capture,
            text=True,
            env=environment,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BackupContractError("PostgreSQL command failed") from exc
    return completed.stdout.strip() if capture else ""


def connection_arguments(config: DatabaseConfig) -> list[str]:
    return [
        "--host",
        config.host,
        "--port",
        str(config.port),
        "--username",
        config.user,
        "--dbname",
        config.database,
        "--no-password",
    ]


def query_scalar(
    config: DatabaseConfig,
    query: str,
    *,
    psql_bin: str,
    runner: Runner,
) -> str:
    return runner(
        [psql_bin, *connection_arguments(config), "--tuples-only", "--no-align", "--command", query],
        config.password,
        True,
    ).strip()


def ensure_outside_repository(path: Path) -> Path:
    resolved = path.resolve()
    if resolved == REPOSITORY_ROOT or REPOSITORY_ROOT in resolved.parents:
        raise BackupContractError("Backup artifacts must be outside the repository")
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
