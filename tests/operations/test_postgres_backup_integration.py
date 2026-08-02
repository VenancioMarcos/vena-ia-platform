import os
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest
from psycopg import connect, sql

from scripts.backup_contract import DatabaseConfig
from scripts.postgres_backup import create_backup
from scripts.postgres_restore import restore_backup


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_BACKUP_INTEGRATION") != "1",
    reason="PostgreSQL backup integration is explicitly enabled",
)


class DockerPostgresRunner:
    def __init__(self, container_id: str) -> None:
        self.container_id = container_id

    def _inside(self, command: list[str], *, capture: bool) -> str:
        completed = subprocess.run(
            [
                "docker",
                "exec",
                self.container_id,
                "sh",
                "-c",
                'export PGPASSWORD="$POSTGRES_PASSWORD"; exec "$@"',
                "postgres-tools",
                *command,
            ],
            check=True,
            capture_output=capture,
            text=True,
        )
        return completed.stdout.strip() if capture else ""

    def __call__(self, command: list[str], _password: str, capture: bool) -> str:
        tool = Path(command[0]).name
        arguments = command[1:]
        container_backup = f"/tmp/vena-backup-{uuid4().hex}.dump"
        if tool == "pg_dump":
            output_index = arguments.index("--file") + 1
            host_backup = Path(arguments[output_index])
            arguments[output_index] = container_backup
            try:
                self._inside([tool, *arguments], capture=False)
                subprocess.run(
                    ["docker", "cp", f"{self.container_id}:{container_backup}", str(host_backup)],
                    check=True,
                )
            finally:
                self._inside(["rm", "-f", container_backup], capture=False)
            return ""
        if tool == "pg_restore":
            host_backup = Path(arguments[-1])
            subprocess.run(
                ["docker", "cp", str(host_backup), f"{self.container_id}:{container_backup}"],
                check=True,
            )
            arguments[-1] = container_backup
            try:
                return self._inside([tool, *arguments], capture=capture)
            finally:
                self._inside(["rm", "-f", container_backup], capture=False)
        return self._inside([tool, *arguments], capture=capture)


def test_postgresql_backup_restore_round_trip(tmp_path: Path) -> None:
    container_id = os.environ["POSTGRES_CONTAINER_ID"]
    password = os.environ["POSTGRES_PASSWORD"]
    source_database = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    target_database = "vena_ia_restore_test"
    admin_url = f"postgresql://{user}:{password}@localhost:5432/postgres"
    source_url = f"postgresql://{user}:{password}@localhost:5432/{source_database}"
    target_url = f"postgresql://{user}:{password}@localhost:5432/{target_database}"
    runner = DockerPostgresRunner(container_id)
    source = DatabaseConfig("localhost", 5432, source_database, user, password)
    target = DatabaseConfig("localhost", 5432, target_database, user, password)

    with connect(source_url, autocommit=True) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS backup_integrity_probe "
            "(id integer PRIMARY KEY, value text NOT NULL)"
        )
        connection.execute(
            "INSERT INTO backup_integrity_probe (id, value) VALUES (1, 'verified') "
            "ON CONFLICT (id) DO UPDATE SET value = EXCLUDED.value"
        )

    backup, manifest = create_backup(
        tmp_path,
        source,
        application_version="1.2.0",
        runner=runner,
    )
    assert backup.is_file()

    with connect(admin_url, autocommit=True) as connection:
        connection.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target_database)))
        connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_database)))
    try:
        restore_backup(
            manifest,
            target,
            confirmed_database=target_database,
            allowed_database=target_database,
            runner=runner,
        )
        with connect(target_url) as connection:
            restored = connection.execute(
                "SELECT value FROM backup_integrity_probe WHERE id = 1"
            ).fetchone()
            migration = connection.execute(
                "SELECT version_num FROM alembic_version"
            ).fetchone()
        assert restored == ("verified",)
        assert migration == ("f42a1b7c9d30",)
    finally:
        with connect(admin_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target_database))
            )
