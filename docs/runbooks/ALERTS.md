# Runbook — Internal Alert Contracts

**Delivery:** no-op/local only
**External calls:** none

## Contract

Alert events contain only severity, a closed event code, correlation ID, UTC
timestamp and allowlisted operational context. Context keys are limited to
dependency, operation, normalized route, status class and scope. Tokens, cookies,
passwords, keys, user/domain identifiers and user content are never accepted.

Supported codes:

- `dependency_unavailable`;
- `repeated_auth_failure_threshold`;
- `rate_limit_threshold`;
- `backup_job_failed`;
- `restore_failed`;
- `readiness_degraded`;
- `ai_provider_unavailable`;
- `processing_failure_threshold`;
- `unexpected_internal_error`.

`AlertManager` applies basic deduplication/cooldown by code plus safe context.
`OBSERVABILITY_ALERT_COOLDOWN_SECONDS` defaults to 30 seconds. Provider failure is
contained and never changes the primary API response.

## Operator response

1. Capture the event code, severity and correlation ID.
2. Query correlated audit rows and structured logs without copying user content.
3. Use `/ready` to identify only the dependency state.
4. Follow the relevant recovery or authentication runbook.
5. Record the outcome through the normal incident process.

No webhook, e-mail, Slack, PagerDuty, SaaS, purchase or message delivery exists in
this package. A real provider requires a separate authorization and security
review; the local contract is not evidence that notifications are delivered.
