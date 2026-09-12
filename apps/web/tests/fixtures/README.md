# Synthetic turning v3 fixtures

These three TypeScript constants are actual serialized results from the existing
Python service and STEP E2E inputs. They are not HTTP responses from a deployed
turning route. No route or viewer is added by AUTO-023.

| File | Real input variation | Status |
| --- | --- | --- |
| cylinder-success.ts | cylinder_d50_l100, original E2E parameters | SUCCESS_SYNTHETIC |
| quantized-violation.ts | same STEP, radial allowance 0.50026, zone R26.5004..26.5006/Z-60..-50 | QUANTIZED_BOUNDARY_VIOLATION |
| reconstruction-failure.ts | same STEP, radial allowance 9.99999 and clearance 0.00001 | QUANTIZED_VERIFICATION_FAILED |

The generator reuses the three setups from test_turning_pipeline_e2e.py and the
real orchestrator, without monkeypatches. Timestamp is fixed at 2026-09-09 UTC.
Hashes and binding version are preserved, not invented. Each payload is validated
again by SyntheticTurningExecutionResult.model_validate_json. Reproduce from repo root:

```powershell
.venv\Scripts\python.exe apps/web/tests/fixtures/generate_turning_fixtures.py --check
```

Omit --check only when deliberately regenerating after reviewed backend changes.
Check mode compares the serialized files and freshly replayed model values.
BRep serialization can differ across OCCT versions; investigate differences,
do not replace hashes to hide drift. Generator requires existing backend test
dependencies, adds none and changes no Python production contract.

The readonly constants use `as const satisfies SyntheticTurningExecutionResult`.
`tests/turning-contracts.typecheck.ts` includes 12 expected compile failures and
exhaustive narrowing across seven states. Run the existing web typecheck script
or the installed TypeScript binary with --noEmit. These tests are not UI code.

AUTO-025 adds 14 runtime checks using the installed TypeScript compiler and
Node's built-in test runner, without an additional package. From `apps/web`:

```powershell
node node_modules/typescript/bin/tsc tests/turning-contracts.test.ts --outDir ../../temp/auto025-web-tests --module commonjs --target ES2020 --moduleResolution node --esModuleInterop --strict --skipLibCheck --noEmitOnError --typeRoots node_modules/@types --types node
if ($LASTEXITCODE -eq 0) { node --test ../../temp/auto025-web-tests/tests/turning-contracts.test.js }
```

Output stays in ignored `temp/`. Checks cover JSON round trips, finite fixture
numbers, restricted flags, quantization endpoint associations, and all seven
branches of the existing exhaustive presentation probe. The four early failure
samples are typed test constructions, not additional backend fixtures. The
test-only status predicate assumes an already typed result; it cannot validate
unknown JSON. Digest checks verify format, not authenticity or recomputation.
The Python replay above remains the source-equivalence check.

Aliases in turning-contracts.ts map mission vocabulary onto existing Python
objects: TurningCutSegment = TurningToolpathMove (including RAPID/RETRACT),
TurningToolpathOperation = TurningOperationPlan, TurningVerificationBoundaryReport
= TurningVerificationReport, DiameterQuantizationResult = TurningQuantizationReport,
PlanDiameterQuantizationSummary = TurningPlanQuantizationSummary. TurningPoint2D
is the serialized RadialPoint tuple [R,Z]; profile points use radius_mm/z_mm objects.

Static types do not implement Pydantic numeric bounds, finiteness, UTC parsing,
digest consistency or geometric validators. They cannot validate untrusted JSON
or enforce runtime freezing. Defaults are required here because the fixtures
represent complete model_dump output. All physical/output flags remain false;
PASS describes declared synthetic boundaries only. No executable turning NC,
physical collision approval, real controller or network integration is provided.
