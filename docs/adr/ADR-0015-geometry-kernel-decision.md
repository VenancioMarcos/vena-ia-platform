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
