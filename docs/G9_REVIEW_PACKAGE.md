# G9 Review Package v1

**Status:** Implemented for external handoff; non-authoritative

**Contract:** `vena-ia.g9-review-package/v1`

**Task:** TASK-V31-004

## Purpose

The G9 Review Package is a deterministic, read-only consolidation of the evidence a
qualified human reviewer and an independent external validator need. It prevents
manual reconstruction of the controlled run while preserving G9 as an external,
server-side human authority boundary.

The package is returned by the existing authenticated controlled-environment run. It
introduces no persistence, reviewer registry, approval endpoint or machine interface.

## Deterministic binding

The package binds:

- candidate program output hash and canonical candidate artifact hash;
- Digital Thread ID, replay hash and every artifact content hash;
- blind-validation frozen bundle and replay hashes;
- G0-G8 evidence refs and G9 pending evidence ref;
- Level-1 status/replay and Level-2 status/replay;
- contract versions for every Digital Thread artifact;
- machine/controller profile, synthetic postprocessor and verifier identities;
- known limitations and unresolved risks R-049 through R-052.

Its `package_hash` is the SHA-256 of the canonical package payload and its ID is
derived from that hash. Rebuilding the same authorized evidence produces the same
package ID/hash regardless of authenticated user or download-token issue time.

## Human-review protocol

The package describes, but cannot perform, the following review steps:

1. authenticate a qualified reviewer and revalidate active Organization membership;
2. record qualification and conflict-of-interest declaration;
3. recompute package, Digital Thread, blind bundle and candidate hashes;
4. review G0-G8, limitations, unresolved risks and independent external evidence;
5. record reject/request-correction/next-stage disposition in a future separately
   authorized server-side boundary;
6. bind that disposition to exact hashes, versions, time and revocation rules.

Reviewer identity, evidence reference and disposition are deliberately absent from
the public input contract. Extra-field attempts fail validation.

## Independent external-validation protocol

An external validator must return evidence bound to the exact candidate hash:

- simulator identity/version and configuration hash;
- machine/controller configuration;
- stock, workholding, fixture, datum/WCS, tool/holder and offsets;
- collision, kinematic, travel and machine-limit evidence;
- material-removal, remaining-stock, gouge and protected-surface evidence;
- controller-semantics evidence;
- deterministic trace/replay artifacts.

External evidence is input for later human adjudication only. It cannot mutate G9,
readiness or physical authority automatically.

## Fail-closed conditions

Package construction or validation fails for candidate/hash tampering, Digital Thread
tampering, blind replay mismatch, missing G0-G8, forged G9, forged reviewer/evidence
fields, stale lifecycle, version mismatch or broken artifact binding. Current database
membership and Organization isolation continue to protect the authenticated run and
controlled download.

## Safety state

```text
G0-G8=PASS_WITH_BOUNDED_EVIDENCE
G9=PENDING_AUTHORITATIVE_REVIEW
AUTOMATIC_AUTHORITY=FALSE
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

- **Objective:** provide a complete, reproducible handoff for real human review and
  future independent external validation.
- **Scope:** additive read-only contract/service, existing run response, UI summary,
  tamper/authority tests and documentation.
- **Acceptance:** exact hash/version binding, deterministic replay, strict pending G9,
  no new authority path, green backend/frontend gates and clean PR.
- **Next:** CTO review. G9 adjudication, external-system integration and physical-test
  authorization remain separate future missions.
