# Runbook — Backup Retention and Scheduling

**Status:** v1.3 Package 3
**Scope:** encrypted backup sets outside the repository; no real schedule is installed.

## Safety model

Retention operates only on complete `vena-ia-encrypted-*` directories below one
explicit external root. Before planning any deletion it authenticates the set
manifest, verifies every ciphertext checksum and rejects incomplete, inconsistent,
unknown-version or symlinked sets. A missing historical key blocks retention; set
the matching archived key rather than bypassing validation.

The default is always dry-run:

```bash
python -m scripts.backup_retention \
  --root /secure/vena-ia-backups \
  --daily-keep 7 --daily-max-age-days 14 \
  --weekly-keep 5 --weekly-max-age-days 60 \
  --monthly-keep 12 --monthly-max-age-days 400
```

Review the JSON report. Apply requires the exact same authorized root twice:

```bash
python -m scripts.backup_retention \
  --root /secure/vena-ia-backups \
  --confirm-root /secure/vena-ia-backups \
  --apply
```

Protected sets and the last valid set are never removed. A set is selected when
it exceeds class count or age. Deletion first atomically renames complete sets;
an interrupted `.deleting` marker blocks later runs and requires operator review.

## Controlled scheduling

`python -m scripts.backup_job` acquires `.backup-job.lock`, starts only its own
internal worker, enforces a timeout and removes the lock on success/failure. The
worker requires `BACKUP_CONSISTENCY_GUARD=quiesced`; establish a real maintenance
window so PostgreSQL metadata and MinIO objects cannot change during capture.

Example cron entry (example only; do not install without environment/permissions):

```cron
15 2 * * * cd /opt/vena-ia && /opt/vena-ia/.venv/bin/python -m scripts.backup_job --timeout-seconds 3600
```

Windows Task Scheduler action example:

```text
Program: C:\Vena_IA\.venv\Scripts\python.exe
Arguments: -m scripts.backup_job --timeout-seconds 3600
Start in: C:\Vena_IA
```

Use an OS account restricted to the backup root and protected environment file.
Never put passwords or the encryption key in arguments. Codes: `0` success;
argparse returns nonzero for missing configuration, lock conflict, timeout,
worker failure or policy refusal. No daemon, cloud or external scheduler is added.
