# First Controlled CAD-to-G-code Test Path

**Task:** TASK-V31-006

**Classification:** NON_PRODUCTION / REQUIRES_HUMAN_REVIEW

**Physical authority:** FALSE

## Objective and scope

Provide the first repeatable v3.1 test path from a valid CAD upload to a controlled
G-code candidate download while preserving the released safety boundary. The path
uses existing application contracts and does not add v3.2 scope, external deployment,
machine connectivity or physical authority.

## Gap check

- The backend already implemented the complete authenticated orchestration and
  controlled download, but route coverage mocked the CAD service.
- The web interface did not display Manufacturing Geometry, Process Plan, Toolpath,
  Level-2 and detailed Digital Thread artifact evidence.
- Candidate download displayed warnings but did not require an explicit
  non-production acknowledgement.
- The repository and GitHub metadata contain no deployment configuration,
  environments, deployments, action secrets or variables for an approved external
  web target. The existing local web boundary is therefore the shortest safe target.

## Controlled path

1. Generate a valid STEP cylindrical body at test runtime using the official OCCT
   kernel dependency; no expected features are supplied to the implementation.
2. Authenticate a database-backed user with active Organization/project membership.
3. Upload the STEP body through the real Documents API and in-memory test storage.
4. Execute the real CAD kernel, topology/manufacturing evidence, verified process
   planning, bounded toolpath, synthetic candidate generation, Level-1/Level-2,
   blind validation, G0-G8 and Digital Thread services.
5. Revalidate the controlled download proof and candidate content through the real
   download route.
6. In browser coverage, review each evidence group and explicitly acknowledge
   NON_PRODUCTION, required human review and absence of physical authority before
   enabling download.

## Evidence and acceptance

- The backend integration test proves actual upload-to-download service wiring with a
  valid CAD body and no mocked CAD result.
- Desktop and reduced-width browser tests prove reviewable evidence and guarded
  download UX.
- G9 remains `PENDING_AUTHORITATIVE_REVIEW`.
- `CAD_TO_GCODE_CONTROLLED_VALIDATION_READY=FALSE`.
- `PHYSICAL_USE_AUTHORIZED=FALSE`.
- No machine-send, DNC/NC transfer, cycle start, direct machine control or human-review
  bypass exists or was exercised.

## Known limitations and next evidence

- The first body is cylindrical but the released candidate path is 3-axis/2.5D
  milling; this test does not claim turning or facing validation.
- A representative corpus of prismatic, holes/pockets, contouring and turning parts
  remains required before broader controlled-validation readiness can be considered.
- Browser automation verifies the UI contract with deterministic API fixtures, while
  the backend test independently verifies the full real service chain.
- External hosted deployment and independent external simulation remain separate
  owner/CTO-authorized work.

## Delivery record

- **Objective:** first controlled CAD-to-G-code test path.
- **Files:** backend integration test, web evidence/review controls, contracts,
  browser tests and project governance documents.
- **Tests:** focal backend integration, frontend typecheck/build and browser coverage;
  full regression is the release gate for the Draft PR.
- **Acceptance:** repeatable real backend chain, reviewable browser evidence and all
  safety invariants preserved.
- **Next step:** CTO review of the Draft PR; no new phase starts automatically.
