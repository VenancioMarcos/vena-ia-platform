# CAD feature recognition v1

## Contract

`vena-ia.geometry-features/v1` is an additive field of the authenticated STEP
analysis response. It reports kernel/version, shape class, rule version, closed
confidence classes, evidence, dimensions with units/source/status, local topology
references, uncertainty and limitations. Every result is marked
`PRELIMINARY_GEOMETRIC_FEATURE_REQUIRES_HUMAN_REVIEW`.

## Rule 1.0.0

The recognizer consumes the already loaded OCCT shape; it does not parse or load
STEP a second time. Results are sorted by stable geometric keys before local
`feature-NNNN` identifiers are assigned.

Supported:

* `PLANAR_FACE`: OCCT `GeomAbs_Plane`, area and oriented normal;
* `CYLINDRICAL_FACE`: OCCT `GeomAbs_Cylinder`, radius, diameter, axis, extent and area;
* `THROUGH_CYLINDRICAL_HOLE`: only an inward-oriented, axis-aligned constant-radius
  cylindrical boundary whose two axial endpoints coincide with opposite limits of
  the topological envelope.

Deferred:

* closed/blind holes, because a robust bottom/adjacency proof is not yet implemented;
* simple slots, because no restricted definition and sufficient corpus exist;
* pockets, bosses, threads, gears, freeform/spline and pattern recognition.

A cylindrical primitive never becomes a hole without the stricter evidence. A
planar primitive never becomes a pocket. The rule infers no design or manufacturing
intent.

## Tolerance and references

Rule tolerance is `1e-6` in the STEP length unit and is used only for geometric
comparison in the validated synthetic corpus. It is not GD&T, drawing tolerance,
process capability or machine accuracy. `face:N:LOCAL_ANALYSIS_REFERENCE` is local
to one execution and is not stable across kernel or rule versions.

## Corpus and evidence

The executable corpus creates geometry with OCCT at test time; no proprietary CAD
is stored. It covers a box, external cylinder, axis-aligned through bore, blind bore,
invalid topology, malformed STEP and deterministic replay. Expected/observed rules
are summarized in `CAD_FEATURE_VALIDATION_EVIDENCE.json`.

False-positive gates prove that an external cylinder is not a hole, a planar face
is not a pocket, a blind bore is not a through hole and invalid topology emits no
feature. The supported through bore proves the false-negative gate and validates
diameter/depth within the declared tolerance.

## Boundaries

Traversal is capped at 10,000 faces and reuses the Package 2 50 MiB input limit.
STL, DXF and IGES remain `PLANNED`; no superficial parser is provided. The contract
may be a future engineering-planning input, but no machine/tool selection, CAM,
toolpath, G-code, manufacturability or CNC transmission is activated.

## Integrated workflow reuse

The v2.0 Package 1 workflow reuses the `CADDocumentAnalysis` already produced for
geometry and features; `FeaturePlanningBridge.plan_from_analysis()` does not reload
or reparse STEP. Only the existing `THROUGH_CYLINDRICAL_HOLE` rule may produce a
`DRILLING_CANDIDATE`. Other primitives remain `BLOCKED_UNSUPPORTED_FEATURE`, and no
feature result establishes process validity or production readiness.
