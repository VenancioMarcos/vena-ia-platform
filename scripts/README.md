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
