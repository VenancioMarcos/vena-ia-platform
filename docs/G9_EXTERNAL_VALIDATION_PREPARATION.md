# G9 External Validation Preparation

**Status:** Prepared evidence boundary; G9 remains pending

**Task:** TASK-V31-003

**Applies to:** `vena-ia.controlled-test-environment/v1`

## Purpose

This document defines what is still required before an authoritative human reviewer
can adjudicate G9. It does not create a G9 approval mechanism, reviewer authority,
physical authorization or permission to use candidate G-code on a machine.

The current controlled environment proves G0-G8 only. Every artifact remains
`CANDIDATE_FOR_VALIDATION`, `NON_PRODUCTION` and `REQUIRES_HUMAN_REVIEW`.

## Evidence classification

### Automatically producible

- immutable hashes and replay evidence for CAD, topology, Manufacturing Geometry,
  process plan, bounded toolpath, synthetic G-code and Level-1/Level-2 verification;
- blind-validation bundle, sealed-reference hash and G0-G8 gate results;
- Digital Thread ownership, schema versions, provenance, lifecycle and references;
- current token identity, active database membership and Organization scope;
- controlled-download signature, expiry, candidate hash and fail-closed denial logs.

Automatic evidence can establish integrity and bounded deterministic behavior. It
cannot identify a qualified reviewer, adjudicate the sealed reference, resolve G9 or
authorize physical use.

### Requires authorized human review

An authoritative review record must be created only by a separately authorized,
server-side mechanism and must bind all of the following:

1. authenticated reviewer identity and active Organization role;
2. reviewer qualification and declared conflict-of-interest status;
3. exact Digital Thread ID, frozen bundle hash and candidate G-code hash;
4. reviewed schema/tool/postprocessor/verifier versions;
5. disposition: reject, request correction or approve for the specifically authorized
   next validation stage;
6. findings for omissions, false positives, process divergence and toolpath divergence;
7. timestamp, immutable evidence reference and revocation/supersession rules.

No review authority may come from payload, frontend state, query, header, hash, HMAC
proof or replay. A hash proves integrity only. The current API intentionally exposes
no G9 transition endpoint.

### Requires external simulation or validation

Before G9 can be adjudicated, evidence must come from an independent, explicitly
selected validation environment and be bound to the same candidate hashes:

- simulator/vendor and version, machine/controller profile and configuration hash;
- verified controller semantics for every emitted RS274 word;
- stock, workholding, fixture, datum/WCS, tool assembly and offsets used in simulation;
- full tool/holder/fixture/workpiece collision evaluation;
- machine travel, kinematics, limits, feeds, spindle and alarm results;
- material-removal comparison, remaining stock, gouge and protected-surface results;
- deterministic log/report, screenshots or trace artifacts and final result hash;
- independent confirmation that the tested program exactly matches the candidate.

The existing synthetic postprocessor and bounded Level-2 verifier do not satisfy this
external evidence category by themselves.

### Required before any physical test

Even after external simulation and G9 review, physical use remains prohibited until a
separate Owner-authorized protocol records machine compatibility, a real validated
postprocessor/controller target, tooling/workholding inspection, risk assessment,
qualified personnel, safe setup/E-stop checks, rollback/emergency procedure and an
explicit physical-use authorization bound to the exact reviewed hashes.

That protocol is outside TASK-V31-003. No physical test is authorized here.

## Fail-closed verification

The controlled download revalidates active membership, Organization ownership,
proof signature and expiry, complete artifact hashes, RS274 replay, blind evidence,
G0-G8, G9 pending and Digital Thread replay. Tests additionally prove that:

- query/header flags do not change G9 or physical authority;
- a G9 field injected in the request body is rejected;
- a valid HMAC proof remains download integrity evidence only;
- cross-Organization and revoked-membership access fail closed;
- expired proof, candidate tampering, thread tampering and forged G9 fail closed.

Repeated valid download is still a candidate export; replay cannot promote G9 or
physical authority.

## Terminal state

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

## Delivery record

- **Objective:** prepare the evidence path to G9 and external validation without
  granting G9 or physical authority.
- **Scope:** audit G0-G8, authority vectors, tenancy and controlled download; classify
  evidence still required for human, external and physical stages.
- **Files:** this document plus the project context, roadmap, decision, risk,
  authorization, changelog and CTO status records; focused tests extend the existing
  controlled-environment suite.
- **Tests:** Ruff, mypy, focused controlled-environment tests and full backend pytest.
- **Acceptance:** G9 remains pending; client/HMAC/replay cannot grant authority;
  cross-Organization, revoked membership, expired proof and tampering fail closed.
- **Next step:** CTO review. Any G9 mechanism, external simulator integration or
  physical-test protocol requires a separate explicit mission.
