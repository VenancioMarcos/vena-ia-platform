# Vena_IA Platform v1.8.0 — CAD Interoperability and Feature Recognition

**Status:** published; no deploy

## Highlights

* OpenCascade Technology 7.9.3 is integrated through pinned
  `cadquery-ocp==7.9.3.1.1` behind a lazy Modular Monolith adapter.
* Authenticated STEP analysis adds topological bounding box, surface area, solid
  volume, validity and shape classification to the preserved textual metadata.
* `vena-ia.geometry-features/v1` rule `1.0.0` recognizes planar/cylindrical
  primitives and strict axis-aligned through cylindrical holes with local evidence.
* `vena-ia.feature-planning/v1` rule `1.0.0` maps only validated through holes to a
  non-executable `DRILLING_CANDIDATE` and reuses Engineering v1.7 only after explicit
  material, machine and tool selection.

## Safety and review

Every feature and planning result requires human review. Closed holes, slots,
pockets and ambiguous geometry are deliberately not classified. Geometric confidence
does not establish manufacturing intent, tolerance, process capability or safety.
R-019, R-038, R-040 and R-041 remain residual/monitored.

There is no executable CAM, toolpath, stock/setup strategy, postprocessor, G-code,
M-code, NC file, CNC transmission, machine control or automatic manufacturability
claim. This release candidate performs no deploy.

## Validation evidence

Synthetic and reproducible corpus covers box, external cylinder, one/two through
holes, blind hole, invalid topology, malformed input and deterministic replay.
Contracts preserve kernel, feature-rule, planning-rule, Engineering-rule and catalog
traceability. The release candidate gate requires Ruff, mypy, pytest, frontend,
OpenAPI, Alembic head `c27f6d9e4a10`, runtime policy, Compose and all applicable CI.

## Publication

PR #19 was integrated by Squash Merge after direct owner authorization. The annotated
tag `v1.8.0` and GitHub Release were published. No deploy or CNC production action
was performed; v1.9 starts only from its documented Package 1 scope.
