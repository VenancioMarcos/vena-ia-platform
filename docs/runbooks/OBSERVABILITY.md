# Runbook — Structured Observability Package 1

**Schema:** `vena-ia.observability/v1`
**External telemetry:** disabled / not implemented

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
