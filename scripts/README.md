# Scripts

Scripts operacionais do projeto.
# Operational scripts

Operational automation is versioned here; generated data is never versioned.

PostgreSQL backup and restore:

```bash
python -m scripts.postgres_backup --output-directory /secure/outside/repository
python -m scripts.postgres_restore \
  --manifest /secure/outside/repository/vena-ia-postgres-YYYYMMDDTHHMMSSZ.manifest.json \
  --target-database vena_ia_restore \
  --confirm-target vena_ia_restore \
  --allow-database vena_ia_restore
```

Passwords are read from `POSTGRES_PASSWORD` and passed to PostgreSQL tools only
through `PGPASSWORD`; they are never placed in command arguments or manifests.
See `docs/runbooks/POSTGRES_BACKUP_RESTORE.md` for the controlled procedure.

MinIO backup and restore use the same external artifact boundary:

```bash
python -m scripts.minio_backup --output-directory /secure/outside/repository
python -m scripts.minio_restore \
  --manifest /secure/outside/repository/vena-ia-minio-TIMESTAMP-ID/manifest.json \
  --target-bucket vena-ia-restore \
  --confirm-target vena-ia-restore \
  --allow-bucket vena-ia-restore
```

`MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` and `MINIO_BUCKET` are
read from the environment. PostgreSQL and MinIO manifests may be joined by
`vena-ia.backup-set/v1`; inconsistent sets are rejected and never auto-repaired.

Package 3 creates authenticated encrypted sets and never places key material in
arguments or manifests:

```bash
python -m scripts.backup_job --timeout-seconds 3600
python -m scripts.encrypted_restore \
  --index /secure/vena-ia-backups/vena-ia-encrypted-UUID/encrypted-set.json \
  --output-directory /secure/disposable-restore/UUID
python -m scripts.backup_retention --root /secure/vena-ia-backups
python -m scripts.backup_retention \
  --root /secure/vena-ia-backups \
  --confirm-root /secure/vena-ia-backups \
  --apply
```

The first retention command is the mandatory dry-run. `backup_job` reads database,
MinIO and AES-256-GCM key settings exclusively from the environment, requires a
quiesced consistency window, uses a lock and removes plaintext staging. See the
backup, retention and recovery runbooks before enabling an OS scheduler.
