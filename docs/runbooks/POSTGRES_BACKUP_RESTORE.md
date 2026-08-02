# Runbook — PostgreSQL and MinIO Backup and Restore

**Status:** v1.3 Package 2
**Scope:** PostgreSQL/pgvector, MinIO and cross-store consistency.

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
  --application-version 1.3.0
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
MinIO recovery and cross-store consistency are defined below. Scheduling,
automatic retention and external storage remain later v1.3 work.

## MinIO contract and restore

`python -m scripts.minio_backup` creates `vena-ia.minio-backup/v1`, one external
artifact per object and a deterministic JSON manifest. Each object records key,
byte size, SHA-256, content type, UTC modification time, trustworthy single-part
ETag when available, and project/document identifiers derivable from its key.
Contents and credentials never enter the manifest.

```bash
python -m scripts.minio_backup \
  --output-directory /secure/vena-ia-backups \
  --bucket vena-ia-files \
  --application-version 1.3.0-dev \
  --backup-set-id UUID-SHARED-WITH-POSTGRES
```

Restore validates the complete manifest and every artifact before mutation. The
destination bucket or controlled prefix must be empty and match confirmation and
allowlist exactly.

```bash
python -m scripts.minio_restore \
  --manifest /secure/vena-ia-backups/vena-ia-minio-TIMESTAMP-UUID/manifest.json \
  --target-bucket vena-ia-restore \
  --confirm-target vena-ia-restore \
  --allow-bucket vena-ia-restore
```

Traversal, symlink, overwrite, contract/version, size or checksum errors fail
closed. Partial writes are cleaned from a disposable destination.

## Backup-set consistency

`vena-ia.backup-set/v1` binds PostgreSQL and MinIO manifests with the same UUID,
UTC timestamp and application version. It records Alembic head, manifest
checksums and counts. Missing, orphaned or cross-project objects fail without
automatic repair. CI creates disposable metadata/content, backs up both stores,
simulates loss, restores into a new database and bucket, verifies them and cleans up.

## Retention, discard, encryption, RPO and RTO

- initial class: `non-production-manual`, expiration target 30 days;
- discard only after another complete set passes a restore drill;
- encryption must use destination/platform controls plus approved key management;
  application-level improvised encryption is forbidden;
- RPO is the age of the last verified complete set;
- RTO must be measured before pilot and is not guaranteed by this package.

Package 3 operationalizes these controls through
`vena-ia.encrypted-backup-set/v1`, AES-256-GCM, `scripts.backup_job` and
`scripts.backup_retention`. Procedures and limits are authoritative in
`BACKUP_RETENTION_AND_SCHEDULING.md` and `RECOVERY_DRILL.md`.
