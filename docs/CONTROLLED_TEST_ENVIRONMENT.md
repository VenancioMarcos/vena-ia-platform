# Controlled Test Environment — TASK-V31-002

**Status:** Implemented — awaiting CTO review
**Classification:** `NON_PRODUCTION / REQUIRES_HUMAN_REVIEW`

## Objective

Expose one authenticated, organization-scoped path from an authorized STEP document
through deterministic CAD evidence, Manufacturing Geometry, verified process plan,
bounded toolpath, synthetic postprocessor, Level-1/Level-2 verification, sealed blind
evidence, immutable Digital Thread and controlled candidate download.

## Server-side chain

```text
authorized CAD document
→ topology evidence
→ manufacturing geometry + verified process plan
→ bounded toolpath candidate
→ synthetic RS274 candidate
→ independent Level-1 + bounded Level-2 evidence
→ sealed blind evidence G0–G9
→ immutable Digital Thread
→ short-lived authenticated controlled download
```

`POST /engineering/controlled-environment/runs` creates the evidence chain;
`POST /engineering/controlled-environment/download` revalidates it. Both require a
valid session and active database membership in the requested organization. Catalog
resources must belong to the same organization.

The download proof is HMAC-authenticated, short-lived and bound to user, organization
and canonical hashes of the complete candidate, blind evidence and Digital Thread.
Download revalidates
the proof, G-code hash/manifest, independent RS274 verifier, blind bundle/replay,
G0–G8, G9 pending, organization ownership and Digital Thread replay.

## Required human inputs

Stock bounds, manufacturing intent, catalogs, fixture and datum/WCS statements, tool
geometry, machine envelope, clearance/retract/feed and sealed holdout reference are
explicit inputs. Missing or inconsistent evidence fails closed; geometry does not
silently infer these facts.

## Permanent safety boundary

`G9=PENDING_AUTHORITATIVE_REVIEW` is immutable in this contract. The browser cannot
approve G9. Request bodies, headers and frontend state cannot grant identity, role,
membership, production authority or physical authority.

The `.candidate.nc` download does not imply validated real-machine G-code,
machine-send, DNC/NC transfer, cycle start, direct CNC control, exact B-Rep removal,
machine kinematics, production approval or bypass of human review.

`PHYSICAL_USE_AUTHORIZED=false` remains mandatory.

## Delivery record

### Objective

Implement the controlled, evidence-linked v3.1 test environment authorized by
TASK-V31-002.

### Scope

Backend orchestration, fail-closed download proof/revalidation, authenticated UI,
Digital Thread integration, tests and documentation. No migration or persistence.

### Created files

- `apps/api/app/modules/engineering/controlled_environment.py`
- `apps/api/app/modules/engineering/controlled_environment_schemas.py`
- `apps/web/components/controlled-test-environment.tsx`
- `apps/web/tests/e2e/controlled-environment.spec.ts`
- `docs/CONTROLLED_TEST_ENVIRONMENT.md`
- `docs/adr/ADR-0036-controlled-test-environment.md`

### Acceptance criteria

G0–G8 pass deterministic checks; G9 remains pending; replay/hash/tenancy tampering
fails closed; only candidate download exists; physical actions and review bypass are
absent.

### Next step

CTO review of the Draft PR and CI. No v3.2, merge, release, deploy or physical test is
authorized by this delivery.
