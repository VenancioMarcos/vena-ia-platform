# Vena_IA Platform v1.9.0 — Controlled Pilot Readiness

**Status:** published; no deploy

## Organizational foundation

Organizations, Teams and persistent OWNER/ADMIN/MEMBER memberships establish a
minimal organizational boundary for synthetic pilot preparation. Owner bootstrap is
transactional, revocation is checked against the database and Pilot Context plus its
readiness/privacy checklist remain scoped to the authorized organization and team.

Authorization is fail-closed: `TOKEN + DATABASE = AUTHORITY`. Request bodies,
queries, `X-User-ID`, `X-Role` and arbitrary headers never grant identity or role.
Cross-organization and cross-team access returns `404`; MEMBER cannot perform
administrative rehearsal operations. Migration head is `d39a7b2c5e11`.

## Controlled synthetic rehearsal

`vena-ia.pilot-evidence/v1` composes allowlisted references to restore, incident,
observability, resilience, capacity, privacy and support evidence. All evidence is
synthetic/non-production. Closed states make incomplete, partial, unavailable or
failed mandatory evidence block readiness instead of becoming a false PASS.

Rollback uses `vena-ia.pilot-rollback/v1` with action, target, result, warnings,
reference, timestamp and actor. Partial or failed rollback never becomes success.
`vena-ia.pilot-evidence-integrity/v1` verifies the canonical SHA-256 checksum as
`MATCH`/`MISMATCH`; it proves integrity only, not authorship, identity, signature,
non-repudiation or external trust.

## Virtual CNC validation and human review

`vena-ia.virtual-cnc-plan-validation/v1` accepts only the neutral allowlisted plan
shape and remains `SIMULATION_ONLY=true`, `executable_output=false` and
`human_review_required=true`. It rejects executable payloads, G-code and M-code.
There is no CAM toolpath, coordinate program, postprocessor, NC/DNC file,
transmission, machine target, spindle/motion execution or CNC control.

Every output requires human review. This release candidate does not authorize a
real company, client, external user, real data, real pilot, production SLO/SLA,
external monitoring, paid service, deploy or commercial publication.

## Risks, evidence and limitations

R-042 (organizational isolation/role escalation) and R-043 (false pilot readiness)
remain partially mitigated and monitored. The runbook/evidence mapping is maintained
in `docs/PILOT_EVIDENCE_MATRIX.md`; explicit gaps may not be hidden. Capacity and
SLO references are synthetic technical evidence and cannot be extrapolated to
production. The release candidate preserves all public contracts from v1.2–v1.8.

## Validation

The terminal gate covers Ruff, mypy, full pytest, organizational/rehearsal,
authentication/isolation, neutral CNC validation, Alembic upgrade/downgrade/upgrade,
OpenAPI 1.9.0, frontend typecheck/build, secret scan, runtime policy, Docker Compose
configuration and the Backend, Frontend and Runtime Policy CI workflows.

## Publication

PR #21 was integrated by Squash Merge after the direct Owner Release Gate. The
annotated tag `v1.9.0` and GitHub Release were published from the final release
commit. No deploy is part of this release process.
