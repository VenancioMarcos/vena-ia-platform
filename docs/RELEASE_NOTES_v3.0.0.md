# Vena_IA Platform v3.0.0 — Manufacturing Intelligence & Digital Thread

## Release scope

v3.0.0 adds an immutable, organization-scoped digital-thread manifest across the
controlled CAD-to-G-code evidence chain and a bounded read-only intelligence layer.
Artifacts carry identity, schema version, canonical hash, lifecycle, provenance,
chain refs, replay and verification refs. No persistence migration is required.

## Security and validation

Token plus database membership is authority. Cross-org access, hash mismatch, broken
or forward refs, schema mismatch, stale/revoked state and forged replay fail closed.
Bounded intelligence has no tools or mutation path and cannot alter deterministic
evidence, approve G0–G9 or resolve G9.

## Permanent safety boundary

G9 remains `PENDING_AUTHORITATIVE_REVIEW`.

`CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = FALSE`

`PHYSICAL_USE_AUTHORIZED = FALSE`

All G-code artifacts remain `CANDIDATE_FOR_VALIDATION`, `NON_PRODUCTION` and
`REQUIRES_HUMAN_REVIEW`. No machine-send, NC/DNC, cycle start or machine control is
provided.
