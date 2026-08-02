import io
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from minio import Minio
from psycopg import connect, sql

from scripts.backup_contract import DatabaseConfig
from scripts.backup_set import DocumentReference, create_backup_set_manifest
from scripts.encrypted_backup import EncryptionKey, create_encrypted_bundle, decrypt_bundle
from scripts.minio_backup import create_minio_backup, restore_minio_backup
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


@pytest.mark.skipif(
    os.getenv("RUN_MINIO_BACKUP_INTEGRATION") != "1",
    reason="MinIO backup integration is explicitly enabled",
)
def test_combined_postgresql_minio_backup_restore_round_trip(tmp_path: Path) -> None:
    container_id = os.environ["POSTGRES_CONTAINER_ID"]
    password = os.environ["POSTGRES_PASSWORD"]
    source_database = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    target_database = "vena_ia_combined_restore_test"
    admin_url = f"postgresql://{user}:{password}@localhost:5432/postgres"
    source_url = f"postgresql://{user}:{password}@localhost:5432/{source_database}"
    target_url = f"postgresql://{user}:{password}@localhost:5432/{target_database}"
    runner = DockerPostgresRunner(container_id)
    source = DatabaseConfig("localhost", 5432, source_database, user, password)
    target = DatabaseConfig("localhost", 5432, target_database, user, password)
    minio = Minio(
        os.environ["MINIO_ENDPOINT"],
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
        secure=False,
    )
    suffix = uuid4().hex[:12]
    source_bucket = f"vena-source-{suffix}"
    target_bucket = f"vena-restore-{suffix}"
    project_id = str(uuid4())
    document_id = str(uuid4())
    object_key = f"projects/{project_id}/documents/{document_id}/file.pdf"
    content = b"cross-store-integrity-probe"
    backup_set_id = str(uuid4())
    created_at = datetime.now(timezone.utc).replace(microsecond=0)
    encryption_key = EncryptionKey("ci-recovery-key", bytes(range(32)))
    backup_started = time.perf_counter()

    with connect(source_url, autocommit=True) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS backup_document_probe "
            "(document_id uuid PRIMARY KEY, project_id uuid NOT NULL, object_key text NOT NULL)"
        )
        connection.execute(
            "INSERT INTO backup_document_probe (document_id, project_id, object_key) "
            "VALUES (%s, %s, %s) ON CONFLICT (document_id) DO UPDATE SET object_key = EXCLUDED.object_key",
            (document_id, project_id, object_key),
        )
    minio.make_bucket(source_bucket)
    minio.put_object(source_bucket, object_key, io.BytesIO(content), len(content), "application/pdf")
    try:
        _, postgres_manifest = create_backup(
            tmp_path / "postgres",
            source,
            application_version="1.3.0-dev",
            runner=runner,
            now=created_at,
            backup_set_id=backup_set_id,
        )
        _, minio_manifest = create_minio_backup(
            tmp_path / "minio",
            minio,
            source_bucket,
            application_version="1.3.0-dev",
            now=created_at,
            backup_set_id=backup_set_id,
        )
        combined = create_backup_set_manifest(
            tmp_path / "backup-set.json",
            postgres_manifest,
            minio_manifest,
            [DocumentReference(document_id, project_id, object_key)],
        )
        assert combined.consistency_status == "CONSISTENT"
        encrypted_root, encrypted_index = create_encrypted_bundle(
            tmp_path / "encrypted",
            postgres_manifest,
            minio_manifest,
            tmp_path / "backup-set.json",
            encryption_key,
        )
        backup_duration = time.perf_counter() - backup_started
        assert encrypted_root.is_dir()

        minio.remove_object(source_bucket, object_key)
        with connect(source_url, autocommit=True) as connection:
            connection.execute(
                "DELETE FROM backup_document_probe WHERE document_id = %s", (document_id,)
            )
        shutil.rmtree(tmp_path / "postgres")
        shutil.rmtree(tmp_path / "minio")
        (tmp_path / "backup-set.json").unlink()
        loss_time = datetime.now(timezone.utc)

        with connect(admin_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target_database))
            )
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_database)))
        restore_started = time.perf_counter()
        decrypted = decrypt_bundle(encrypted_index, tmp_path / "decrypted", encryption_key)
        restore_backup(
            decrypted.postgres_manifest,
            target,
            confirmed_database=target_database,
            allowed_database=target_database,
            runner=runner,
        )
        restore_minio_backup(
            decrypted.minio_manifest,
            minio,
            target_bucket,
            confirmed_bucket=target_bucket,
            allowed_bucket=target_bucket,
        )
        with connect(target_url) as connection:
            restored = connection.execute(
                "SELECT document_id::text, project_id::text, object_key "
                "FROM backup_document_probe WHERE document_id = %s",
                (document_id,),
            ).fetchone()
            migration = connection.execute("SELECT version_num FROM alembic_version").fetchone()
        response = minio.get_object(target_bucket, object_key)
        try:
            restored_content = response.read()
        finally:
            response.close()
            response.release_conn()
        assert restored == (document_id, project_id, object_key)
        assert restored_content == content
        assert migration == ("f42a1b7c9d30",)
        restore_duration = time.perf_counter() - restore_started
        rpo_seconds = max(0.0, (loss_time - created_at).total_seconds())
        print(
            "RECOVERY_METRICS="
            + json.dumps(
                {
                    "environment": "github-actions" if os.getenv("GITHUB_ACTIONS") else "local",
                    "objects": 1,
                    "object_bytes": len(content),
                    "backup_seconds": round(backup_duration, 3),
                    "restore_seconds": round(restore_duration, 3),
                    "technical_rpo_seconds": round(rpo_seconds, 3),
                    "production_slo": False,
                },
                sort_keys=True,
            )
        )
        shutil.rmtree(decrypted.root)
    finally:
        for bucket in (source_bucket, target_bucket):
            if minio.bucket_exists(bucket):
                for item in minio.list_objects(bucket, recursive=True):
                    minio.remove_object(bucket, item.object_name)
                minio.remove_bucket(bucket)
        with connect(admin_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target_database))
            )
