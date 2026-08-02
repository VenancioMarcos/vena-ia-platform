# Runbook — Encrypted Cross-store Recovery Drill

**Status:** v1.3 Package 3
**Data class:** disposable test data only

## Preconditions

- PostgreSQL/pgvector and MinIO disposable targets;
- complete encrypted set and its matching external 32-byte key;
- `key_id` selected exactly as recorded by the set;
- empty, explicitly allowlisted database and bucket;
- enough external temporary space for controlled decryption;
- no customer, production or personal data.

## Procedure

1. Authenticate `encrypted-set.json` and all ciphertext artifacts.
2. Decrypt into a new permission-restricted temporary directory with:

   ```bash
   python -m scripts.encrypted_restore \
     --index /secure/backups/vena-ia-encrypted-UUID/encrypted-set.json \
     --output-directory /secure/disposable-restore/UUID
   ```

3. Validate PostgreSQL, MinIO and backup-set manifests before mutation.
4. Create empty disposable database and bucket.
5. Restore PostgreSQL without `--clean`; verify Alembic head.
6. Restore MinIO; verify sizes and SHA-256.
7. Compare document/project storage references and reject missing/orphan objects.
8. Record environment, object count/bytes, backup duration, restore duration,
   technical RPO of this scenario and limitations.
9. Remove decrypted temporary content, disposable database and bucket.

Wrong/missing key, unknown algorithm, corrupted ciphertext, tampered manifest,
partial set, nonempty target or isolation mismatch must fail closed. On failure,
remove plaintext partial output and inspect any `.deleting` marker before retry.

## Metrics and interpretation

The CI integration prints one `RECOVERY_METRICS` JSON line. `backup_seconds` and
`restore_seconds` are observed durations for its tiny disposable dataset;
`technical_rpo_seconds` is the elapsed time between snapshot timestamp and
simulated loss. These values are evidence of reproducibility, not production RPO,
RTO, SLO, capacity or pilot approval. Repeated drills on representative approved
infrastructure are required before real data.

Observed evidence on GitHub Actions run `30745399876` (2026-08-02): one object,
27 bytes; backup `0.409 s`; restore `0.415 s`; scenario technical RPO `1.262 s`;
194 API tests and 43 operational tests passed. This tiny probe is reproducibility
evidence only and must not be extrapolated to production capacity or SLOs.

## Key rotation

Create a new random 32-byte key in the external secret manager and advance the
non-sensitive `BACKUP_ENCRYPTION_KEY_ID`. New sets use the new key. Retain each
old key, access policy and restore test for at least as long as any matching set.
To restore an old set, provide its matching key and ID for that drill only. Never
rewrite a manifest to pretend a different key ID.
