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
