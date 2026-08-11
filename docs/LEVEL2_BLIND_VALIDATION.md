# Level-2 and Controlled Blind Validation

## Objective and scope

Package 3 adds bounded evidence after the independent toolpath and RS274 checks. It
does not add a machine runtime, persistence, exact CAM simulation or physical use.

## Contracts and behavior

`vena-ia.level2-material-removal-evidence/v1` reconstructs every candidate segment
locally. It rejects invalid prior evidence, missing/insufficient stock, discontinuity,
non-finite coordinates, incomplete target coverage, protected-envelope gouge, rapid
collision and supplied fixture keep-out collision. Its volume is only a simplified
cylindrical sweep; remaining material and geometric error explicitly remain not
calculated as exact B-Rep.

`vena-ia.controlled-blind-validation/v1` freezes CAD, topology, manufacturing model,
process plan, toolpath, G-code candidate and Level-2 hashes before later adjudication.
The request contains a sealed-reference hash, never an expected feature/operation
list. Omissions, false positives and process/toolpath divergence stay pending until
sealed human adjudication.

## Gates

G0 CAD integrity; G1 topology; G2 manufacturing model; G3 planning verification;
G4 authorized-resource compatibility; G5 toolpath verification; G6 postprocessor
identity; G7 RS274 verification; G8 Level-2 evidence; G9 real human review. All must
pass for controlled-validation readiness. A missing G9 is `PENDING_REVIEW`, never an
implicit approval.

## Delivery record

Files added/changed: Level-2 and blind schemas/services, authenticated routes, focal
tests and governance documentation. Acceptance covers deterministic PASS, stock and
evidence failures, target omission, trajectory inconsistency, gouge, rapid collision,
fixture keep-out, non-finite coordinates, blind replay and G9 pending. No migration
is needed. Next step is CTO review of Draft PR #28; v3.0 is not started.

`CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = FALSE`

`PHYSICAL_USE_AUTHORIZED = FALSE`
