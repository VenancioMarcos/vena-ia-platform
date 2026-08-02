# Runbook — PostgreSQL Backup and Restore

**Status:** v1.3 Package 1
**Scope:** PostgreSQL/pgvector only; MinIO is a later package.

## Contract

`python -m scripts.postgres_backup` creates a PostgreSQL custom-format dump and
a `vena-ia.postgresql-backup/v1` JSON manifest. The manifest records UTC time,
application version, database/server version, Alembic head, backup set UUID,
file size and SHA-256. It never records password, connection URL or real data.

Artifacts must resolve outside the repository. Existing files are never
overwritten. The Git ignore rules are defense in depth, not an authorization to
store backups in the working tree.

## Required environment

- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`;
- `POSTGRES_PASSWORD`, provided by a secret manager or protected local environment;
- optional `BACKUP_OUTPUT_DIRECTORY` outside the repository;
- optional `BACKUP_RESTORE_ALLOWED_DATABASE` for the disposable restore target.

PostgreSQL 17 client tools (`pg_dump`, `pg_restore`, `psql`) must be available and
compatible with the PostgreSQL/pgvector server. Override their executable paths
only with the explicit CLI options when using a controlled installation.

## Backup

```bash
python -m scripts.postgres_backup \
  --output-directory /secure/vena-ia-backups \
  --application-version 1.2.0
```

Store the dump and its manifest together. Protect access and retention according
to the data classification of the source. This package does not upload, encrypt,
schedule or delete backups.

## Restore drill

Create an empty disposable database whose exact name is explicitly allowed, then:

```bash
python -m scripts.postgres_restore \
  --manifest /secure/vena-ia-backups/vena-ia-postgres-TIMESTAMP.manifest.json \
  --target-database vena_ia_restore \
  --confirm-target vena_ia_restore \
  --allow-database vena_ia_restore
```

Restore fails before mutation when the target/confirmation/allowlist differ,
the target contains user tables, the dump is missing/tampered, the manifest is
invalid, or its checksum/size differs. `pg_restore` runs without `--clean`, so it
cannot silently replace existing objects. After restore, Alembic head must match
the manifest.

## Verification and recovery objectives

The CI drill backs up a test database, restores it to a fresh database, verifies
the checksum, migration head and an integrity probe, then removes the disposable
database. No customer or production data is used.

Initial non-production targets: RPO equals the time since the last manually
verified backup; RTO is not yet guaranteed and must be measured before pilot.
MinIO consistency, encryption, automated retention, scheduling and external
storage remain explicit later work in v1.3.
