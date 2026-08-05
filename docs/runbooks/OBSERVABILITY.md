# Runbook — Structured Observability Packages 1–3

**Schema:** `vena-ia.observability/v1`
**External telemetry:** disabled / not implemented

## Metrics contract

`vena-ia.metrics/v1` is an in-process, thread-safe and replaceable collector.
Collection can be disabled with `OBSERVABILITY_COLLECTION_ENABLED=false`.
Collector exceptions are contained and never fail the primary request.

| Metric | Type | Labels | Unit / buckets |
|---|---|---|---|
| `http_requests_total` | counter | `method`, `route`, `status_class` | requests |
| `http_request_duration_ms` | histogram | `method`, `route`, `status_class` | ms: 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000 |
| `http_internal_errors_total` | counter | `route` | errors |
| `readiness_state` | gauge | `dependency` | 0/1 |
| `dependency_failures_total` | counter | `dependency` | failures |
| `ai_provider_failures_total` | counter | `operation` | failures |
| `processing_jobs_total` | counter | `operation`, `outcome` | jobs |
| `retry_attempts_total` | counter | `operation` | attempts |
| `rate_limits_total` | counter | `scope` | limits |

Allowed routes are API templates, never resolved paths. Methods, status classes,
dependencies, operations, outcomes and scopes use closed values. The following
labels are forbidden: user/project/document identifiers, token, cookie, password,
secret/key, query, body, prompt, response and embedding. Tests call `reset()`;
production restart also resets these ephemeral metrics.

## Metrics API

`GET /internal/metrics` returns JSON with `schema_version` and bounded series. It
is disabled by default (`OBSERVABILITY_METRICS_ENDPOINT_ENABLED=false`). When
enabled, it still requires a valid JWT/cookie and the database role `admin`.
Infrastructure must not expose it publicly; no trusted network is assumed.

## Request context

Clients may send UUIDs in `X-Request-ID` and `X-Correlation-ID`. Valid UUIDs are
preserved; missing or invalid values are replaced. Every response returns both
safe identifiers. Internal services read request-scoped context without headers.

## Event fields

Allowed: UTC timestamp, level, event, schema version, request/correlation IDs,
method, normalized route, HTTP status, duration, application version, environment,
controlled error type and dependency state. Event messages are JSON.

Never log Authorization, Cookie, JWT, password, key, secret, URL with credentials,
request/query/body, document content/path, prompt, question, AI response, embedding,
full hash or stack trace in HTTP responses. The primary control is non-collection;
redaction is defense in depth.

## Health and readiness

- `GET /health`: liveness-compatible response with service and version;
- `GET /ready`: `200 ready` only when PostgreSQL, Redis and MinIO probes pass;
- `GET /ready`: `503 degraded` when any dependency is unavailable.

Readiness exposes only dependency names and `ready`/`unavailable`. It is
preliminary and does not define SLO, capacity or alerting.

## Incident use

1. Capture request/correlation ID from response headers.
2. Filter structured events by those IDs.
3. Compare normalized route, status, duration and controlled error type.
4. Check `/ready` dependency states.
5. Escalate without copying credentials, bodies or document/AI content.

## Audit correlation and local tracing

Security and allowlisted mutation audit rows persist nullable `request_id` and
`correlation_id`; admin queries may filter by either. Existing retention and
event fields remain compatible. Local spans record normalized operation,
span/parent IDs, shared correlation ID, duration, status and controlled error.
The default provider is no-op and there is no exporter.

## Operational limits

Metrics and spans are per-process and ephemeral. They are diagnostic evidence,
not production SLOs, capacity results or historical monitoring. Adding an
external backend, agent, exporter or public route requires a later approved gate.

Package 3 deliberately keeps metrics and spans ephemeral and per process. Restart
loses both; replicas do not aggregate. Persistent security audit remains in
PostgreSQL under `SECURITY_AUDIT_RETENTION_DAYS` (90 days by default), while the
allowlisted drill bundle provides reproducible point-in-time evidence outside the
repository. No external backend or telemetry transport is active. See
`INCIDENT_DRILL.md` and ADR-0023.
