# Feature-to-engineering planning bridge v1

## Purpose

`vena-ia.feature-planning/v1` connects an owned, validated
`vena-ia.geometry-features/v1` feature to preliminary Engineering v1.7 contracts.
It creates non-executable planning candidates; it does not select or approve a
manufacturing process.

The authenticated endpoint is:

`POST /engineering/planning/from-document-feature`

The request references an owned document and deterministic local feature ID. The
server obtains that feature from the existing CAD analysis service and the bridge
consumes the resulting structure; the bridge itself neither parses STEP, invokes
OCCT nor duplicates `FeatureRecognizer`.

## Rule 1.0.0

The allowlist contains one rule:

* `THROUGH_CYLINDRICAL_HOLE` → `DRILLING_CANDIDATE` with status
  `POSSIBLE_NOT_SELECTED` and `executable_output=false`.

`PLANAR_FACE`, `CYLINDRICAL_FACE`, blind/ambiguous/invalid features produce
`NO_PLANNING_CANDIDATE`. In particular, a cylinder never implies drilling or
turning, and a plane never implies approved milling.

Each response preserves document, OCCT, feature-rule, feature ID, planning-rule,
engineering-rule and catalog traceability. `GEOMETRIC_EVIDENCE_CONFIDENCE` and
`PLANNING_CONTEXT_COMPLETENESS` remain separate categorical fields.

## Missing inputs and Engineering reuse

Material, machine and tool IDs must all be explicitly selected before the bridge
calls the existing `EngineeringCatalogService.recommend`; no formula or parameter
engine is copied. Manufacturing intent, drawing tolerance, surface finish, fixture,
coolant and material condition remain required human inputs even when a preliminary
recommendation is available.

Absence is reported as `REQUIRED_INPUT`/`NOT_AVAILABLE`. The existing recommendation
remains `PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW` and may be incompatible or
have unavailable parameters.

## Safety and limits

Only the existing owned document can supply the feature; other-owner and unknown
references fail closed. At most 100 recognized features are inspected per request.
Dimensions must be finite, positive where available, sourced and unit-bearing.

No response contains executable output. CAM strategy, setup, stock, work coordinate
system, toolpath, coordinates, G-code, M-code, postprocessor, NC file, DNC, machine
control, manufacturability or production release remain prohibited.

The synthetic Package 3 corpus is reused. Evidence is summarized in
`FEATURE_PLANNING_VALIDATION_EVIDENCE.json` without retaining CAD or personal data.
