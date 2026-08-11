# ADR-0034 — Independent Level-2 and Controlled Blind Validation

**Status:** Implemented — v2.3 Package 3

## Context

Structural and parser verification do not establish material-removal or controlled
holdout evidence. Promoting them directly would create false physical confidence.

## Decision

Use an independent, bounded Level-2 reconstruction for stock, target coverage,
simplified cylindrical sweep, protected envelopes, rapid motion and supplied fixture
keep-outs. Freeze all deterministic artifacts in a blind harness that receives the
sealed-reference hash but not expected features or operations. Gates G0–G8 are
technical evidence; G9 requires real human-review evidence.

## Consequences

Missing or malformed evidence fails closed and replay is deterministic. Without real
G9 evidence, readiness remains false. The approximation is not exact B-Rep removal,
holder collision, machine kinematics or physical validation and grants no production
or machine authority.
