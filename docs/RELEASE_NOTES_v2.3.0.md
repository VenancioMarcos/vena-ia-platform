# Vena_IA Platform v2.3.0 — Controlled CAD-to-G-code Validation

## Scope

This technical release establishes a bounded, non-production validation chain:

- `vena-ia.toolpath-candidate/v1`;
- `vena-ia.toolpath-verification-evidence/v1`;
- `vena-ia.gcode-candidate/v1`;
- `vena-ia.rs274-safe-subset-verification/v1`;
- `vena-ia.level2-material-removal-evidence/v1`;
- `vena-ia.controlled-blind-validation/v1`.

The postprocessor targets only `VENA_SYNTHETIC_3AXIS_MILL_V1`,
`VENA_RS274_SAFE_SUBSET_V1` and `VENA_SYNTHETIC_3AXIS_POST_V1`. Toolpath, RS274 and
Level-2 verification are independent boundaries with deterministic replay.

## Gates and authority

G0–G8 represent CAD integrity, topology, interpretation, process, resources,
toolpath, postprocessor, RS274 and bounded Level-2 evidence. G9 remains
`PENDING_REVIEW`. The public request cannot supply reviewer identity, review decision
or evidence authority; mass assignment is rejected.

`CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = FALSE`

`PHYSICAL_USE_AUTHORIZED = FALSE`

## Explicit limits

v2.3.0 is not production CAM, validated real-machine G-code or physical CNC
authorization. Level 2 is not exact B-Rep subtraction, holder collision, complete
machine kinematics or physical validation. No machine-send, DNC, automatic NC
transfer, cycle start, direct machine control or human-review bypass exists.

## Validation

The release gate covers Ruff, mypy, Package 1–3 focal tests, G9 negative and mass
assignment tests, CAD/Engineering/auth regressions, OpenAPI, version alignment,
Alembic single head, Docker Compose configuration, diff/secret checks and applicable
GitHub CI workflows.
