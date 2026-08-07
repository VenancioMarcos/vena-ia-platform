# ADR-0015 — Geometry kernel decision

**Status:** Approved with restrictions (B)

OpenCascade Technology is the selected candidate for controlled integration due
to mature STEP/topology capabilities and LGPL-2.1 licensing with exception.
Package 1 does not install it: binary compatibility, Python 3.13, experimental
3.14, Windows, Linux, Docker, supply-chain size and reproducible builds remain
mandatory gates. The Modular Monolith will isolate it behind
`vena-ia.geometry-analysis/v1`.

Until those gates pass, topology, area, volume and tolerance remain
`NOT_AVAILABLE`; the textual STEP parser stays authoritative only for metadata,
points and preliminary envelope. No result asserts manufacturability.

## Package 2 gate

`GO_CONTROLLED_INTEGRATION`: cadquery-ocp 7.9.3.1.1 supplies OCCT 7.9.3 wheels
for CPython 3.13/3.14 and Windows/Linux. It is pinned and imported lazily behind
`OpenCascadeGeometryKernel`. OCCT is LGPL-2.1 with exception; the binding is
Apache-2.0. Native crash/preemptive timeout and 130+ MB transitive wheel footprint
remain restrictions. Tolerance exposed by this package is never manufacturing tolerance.

## Package 3 recognition boundary

Rule `1.0.0` consumes the shape already loaded by the adapter and emits
`vena-ia.geometry-features/v1`. Plane and cylinder are geometric primitives. A
through hole requires an inward-oriented cylindrical boundary and strict axial
envelope traversal. Blind holes and slots are deferred rather than heuristically
classified. All topology references are local and all features require human review.
