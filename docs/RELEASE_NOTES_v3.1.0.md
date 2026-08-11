# Vena_IA Platform v3.1.0 — Controlled CAD-to-G-code Test Environment

## Release classification

This release is `NON_PRODUCTION` and `REQUIRES_HUMAN_REVIEW`. It does not authorize
physical use, machine-send, DNC/NC transfer, cycle start or direct CNC control.

## Controlled flow

v3.1.0 composes the existing authenticated and Organization-scoped path:

CAD → topology evidence → Manufacturing Geometry → Verified Process Plan → bounded
Toolpath → synthetic postprocessor → candidate G-code → Level-1/Level-2 → blind
validation → Digital Thread → controlled candidate download.

The download proof binds the authenticated user, Organization and canonical artifact
hashes. Current membership, signature/expiry, RS274 replay, blind evidence and Digital
Thread replay are revalidated server-side.

## G9 review handoff

`vena-ia.g9-review-package/v1` deterministically consolidates the candidate, every
Digital Thread artifact hash/version, blind bundle, G0-G8, Level-1/Level-2, component
versions, limitations, unresolved risks and human/external validation protocols.

The package is output-only. Reviewer identity, decision and evidence authority are not
accepted from public input. Hash, HMAC and replay prove integrity only.

## Validation boundary

```text
G0-G8=PASS_WITH_BOUNDED_EVIDENCE
G9=PENDING_AUTHORITATIVE_REVIEW
CAD_TO_GCODE_CONTROLLED_VALIDATION_READY=FALSE
PHYSICAL_USE_AUTHORIZED=FALSE
MACHINE_SEND=FALSE
DNC=FALSE
NC_TRANSFER=FALSE
CYCLE_START=FALSE
DIRECT_MACHINE_CONTROL=FALSE
NO_HUMAN_REVIEW_BYPASS=TRUE
```

The synthetic postprocessor is not a real controller postprocessor. Bounded Level-2
evidence is not exact B-Rep, holder or kinematic validation. Qualified human review,
independent external validation and any physical-test authorization remain separate.

No migration, deploy, external simulator integration or machine interface is included.
