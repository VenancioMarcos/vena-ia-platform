# Runbook — Beta 1 Production Readiness

**Status:** Gate Three Phase 1
**Scope:** controlled Internet exposure for five Beta 1 customers.

## Deployment boundary

`docker-compose.production.yml` is a production candidate, not a deployment
authorization. PostgreSQL, Redis and MinIO remain on the private Compose network.
Only API and Web bind to loopback, where an authorized TLS reverse proxy may reach
them. No domain, certificate, VPS, SMTP service or external storage is created by
this repository.

Copy `.env.production.example` to an externally protected `.env.production` and
replace every placeholder. Never commit that file. `APP_ENV=production` makes the
API reject an insecure cookie, a short authentication secret, example database or
MinIO credentials, wildcard/non-HTTPS CORS origins, and in-memory auth/job stores.

## Authorized deployment sequence

1. Provision the owner-approved host, DNS, TLS termination and protected secret
   source.
2. Validate the resolved Compose model:
   `docker compose --env-file .env.production -f docker-compose.production.yml config --quiet`.
3. Start only PostgreSQL, Redis and MinIO; wait for their healthchecks.
4. Run `alembic upgrade head` once from the candidate API image and verify head
   `a71c9e4d2b80` before starting API or workers.
5. Start API and worker; require `GET /health` 200 and `GET /ready` 200.
6. Start Web and configure the TLS reverse proxy. Keep ports 3000 and 8000 bound
   to loopback.
7. Execute the real-browser signup → STEP → review → download → feedback smoke
   against the deployed API. Preserve all CNC physical-use blocks.
8. Run and archive a verified PostgreSQL/MinIO backup and disposable restore drill
   outside the repository before admitting Beta customers.

## Security checks

- `CORS_ORIGINS` contains only the exact HTTPS Web origin.
- Session cookies remain `HttpOnly`, `Secure` and `SameSite=Strict`.
- Registration and login use the Redis-backed fixed-window limits; the production
  values require owner approval based on expected traffic.
- `/internal/metrics` remains disabled unless an authenticated administrative
  access path is separately approved.
- `/ready` must fail with 503 when PostgreSQL, Redis, MinIO or the worker is not
  ready. `/health` is liveness only.
- Database, Redis and MinIO ports must not be published to the Internet.

## Backup and restore for five customers

Use the encrypted, cross-store backup job and the procedures in
`POSTGRES_BACKUP_RESTORE.md`, `BACKUP_RETENTION_AND_SCHEDULING.md` and
`RECOVERY_DRILL.md`. Store encrypted sets outside the repository and host. Before
Beta admission, the owner must approve storage destination, retention, key custody,
schedule, RPO and RTO. A successful disposable restore is mandatory.

## Owner decisions still required

| Item | Required decision | Current state |
|---|---|---|
| Domain and DNS | public Web/API names and DNS operator | `BLOCKED_REAL` |
| Compute | VPS/provider, region, sizing and billing | `BLOCKED_REAL` |
| TLS | certificate issuer/automation and termination proxy | `BLOCKED_REAL` |
| Email | SMTP/provider, sender domain and credentials | `BLOCKED_REAL` |
| Secrets | secret manager, rotation and break-glass custody | `BLOCKED_REAL` |
| Backup | external encrypted target, schedule, retention, RPO/RTO | `BLOCKED_REAL` |
| AI provider | production account, budget and key | `BLOCKED_REAL` |
| Operations | monitoring/alert destination and incident owner | `BLOCKED_REAL` |

No purchase, DNS edit, credential creation, external access grant or deployment may
occur until the owner resolves the corresponding item.
