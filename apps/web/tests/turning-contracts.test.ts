import assert from "node:assert/strict";
import { test } from "node:test";
import type { SyntheticTurningExecutionResult, TurningQuantizationReport } from "../lib/turning-contracts";
import { cylinderSuccess } from "./fixtures/cylinder-success";
import { quantizedViolation } from "./fixtures/quantized-violation";
import { reconstructionFailure } from "./fixtures/reconstruction-failure";
import { presentStage } from "./turning-contracts.typecheck";

type Result = SyntheticTurningExecutionResult;
type Status = Result["pipeline_status"];

// A predicate over already typed results, not a validator for untrusted JSON.
function hasStatus<S extends Status>(result: Result, status: S): result is Extract<Result, { pipeline_status: S }> {
  return result.pipeline_status === status;
}

const fixtures: readonly Result[] = [cylinderSuccess, quantizedViolation, reconstructionFailure];
const earlyMetadata = {
  ...cylinderSuccess.metadata,
  quantization_digest_sha256: null,
  quantized_verification_digest_sha256: null,
};
const early = {
  ...cylinderSuccess, failure_reason: "TEST_STAGE_FAILURE",
  quantization: null, quantized_plan: null, quantized_verification: null,
  metadata: earlyMetadata,
};
// Four branch samples are test-only constructions, not backend exports.
const states = {
  CAD_EXTRACTION_FAILED: {
    ...early, pipeline_status: "CAD_EXTRACTION_FAILED", profile: null, plan: null, verification: null,
    metadata: { ...earlyMetadata, brep_serialization_digest_sha256: null, brep_serialization_format: null, occt_binding_version: null },
  },
  PLANNING_FAILED: { ...early, pipeline_status: "PLANNING_FAILED", plan: null, verification: null },
  BOUNDARY_VERIFICATION_FAILED: { ...early, pipeline_status: "BOUNDARY_VERIFICATION_FAILED", verification: null },
  QUANTIZATION_FAILED: { ...early, pipeline_status: "QUANTIZATION_FAILED" },
  QUANTIZED_VERIFICATION_FAILED: reconstructionFailure,
  QUANTIZED_BOUNDARY_VIOLATION: quantizedViolation,
  SUCCESS_SYNTHETIC: cylinderSuccess,
} satisfies { [S in Status]: Extract<Result, { pipeline_status: S }> };

function checkSerializedValues(value: unknown): void {
  if (typeof value === "number") assert.ok(Number.isFinite(value), "fixture numbers must be finite");
  if (value !== null && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      if (["physical_use_authorized", "executable_output", "is_physical_ready", "is_verified", "is_collision_free", "is_boundary_safe"].includes(key)) {
        assert.equal(item, false, key);
      }
      checkSerializedValues(item);
    }
  }
}

for (const fixture of fixtures) {
  test(`${fixture.pipeline_status}: JSON round trip preserves the complete fixture and restricted flags`, () => {
    checkSerializedValues(fixture);
    const decoded: unknown = JSON.parse(JSON.stringify(fixture));
    assert.deepStrictEqual(decoded, fixture);
    assert.equal(fixture.metadata.schema_version, "synthetic-turning/v3");
    assert.equal(fixture.emission_status, "CONTROLLER_PROFILE_UNRESOLVED");
    for (const [key, digest] of Object.entries(fixture.metadata)) {
      if (key.endsWith("_sha256") && digest !== null) assert.match(String(digest), /^[a-f0-9]{64}$/);
    }
  });

  test(`${fixture.pipeline_status}: quantization endpoints retain their plan associations`, () => {
    assert.ok(fixture.plan && fixture.quantization);
    const moves = fixture.plan.operations.flatMap(operation => operation.moves);
    assert.equal(fixture.quantization.evaluated_moves_count, moves.length);
    assert.equal(fixture.quantization.move_reports.length, moves.length * 2);
    for (const [index, move] of moves.entries()) {
      for (const [endpoint, point] of [move.start_point, move.end_point].entries()) {
        const report: TurningQuantizationReport = fixture.quantization.move_reports[index * 2 + endpoint];
        assert.equal(report.original_radius_mm, point[0]);
        assert.equal(report.reconstructed_radius_mm, report.programmed_x_diameter_mm / 2);
      }
    }
    if (fixture.quantized_plan) {
      assert.equal(fixture.quantized_plan.profile_id, fixture.plan.profile_id);
      assert.equal(fixture.quantized_plan.operations.length, fixture.plan.operations.length);
      fixture.quantized_plan.operations.forEach((operation, index) => {
        const nominal = fixture.plan!.operations[index];
        assert.equal(operation.operation_id, nominal.operation_id);
        assert.equal(operation.moves.length, nominal.moves.length);
      });
      const rebuilt = fixture.quantized_plan.operations.flatMap(operation => operation.moves);
      rebuilt.forEach((move, index) => {
        assert.deepStrictEqual(move.start_point, [fixture.quantization!.move_reports[index * 2].reconstructed_radius_mm, moves[index].start_point[1]]);
        assert.deepStrictEqual(move.end_point, [fixture.quantization!.move_reports[index * 2 + 1].reconstructed_radius_mm, moves[index].end_point[1]]);
      });
    }
  });
}

const expectedPresentation: Record<Status, string> = {
  CAD_EXTRACTION_FAILED: "TEST_STAGE_FAILURE:null",
  PLANNING_FAILED: `${cylinderSuccess.profile.points.length}:TEST_STAGE_FAILURE`,
  BOUNDARY_VERIFICATION_FAILED: `${cylinderSuccess.plan.operations.length}:undefined`,
  QUANTIZATION_FAILED: "PASS",
  QUANTIZED_VERIFICATION_FAILED: `${reconstructionFailure.quantization.evaluated_moves_count}:null`,
  QUANTIZED_BOUNDARY_VIOLATION: `${quantizedViolation.quantized_verification.violating_moves[0]}`,
  SUCCESS_SYNTHETIC: `${cylinderSuccess.quantized_plan.total_cutting_length_mm}`,
};
for (const status of Object.keys(states) as Status[]) {
  test(`${status}: predicate accepts only its branch and exhaustive presentation runs`, () => {
    for (const candidate of Object.values(states)) assert.equal(hasStatus(candidate, status), candidate.pipeline_status === status);
    assert.equal(presentStage(states[status]), expectedPresentation[status]);
  });
}

test("success, violation and internal failure preserve distinct downstream evidence", () => {
  const results: readonly Result[] = Object.values(states);
  const successes = results.filter(result => hasStatus(result, "SUCCESS_SYNTHETIC"));
  assert.equal(successes.length, 1);
  assert.equal(successes[0].quantized_verification.boundary_status, "PASS");
  assert.deepStrictEqual(successes[0].quantized_verification.violating_moves, []);
  assert.equal(successes[0].failure_reason, null);
  const violations = results.filter(result => hasStatus(result, "QUANTIZED_BOUNDARY_VIOLATION"));
  assert.equal(violations.length, 1);
  assert.notEqual(violations[0].quantized_verification.boundary_status, "PASS");
  assert.ok(violations[0].quantized_verification.violating_moves.length > 0);
  const failures = results.filter(result => hasStatus(result, "QUANTIZED_VERIFICATION_FAILED"));
  assert.equal(failures.length, 1);
  assert.equal(failures[0].quantized_plan, null);
  assert.equal(failures[0].quantized_verification, null);
  assert.equal(failures[0].metadata.quantized_verification_digest_sha256, null);
  assert.equal(failures[0].failure_reason, "QUANTIZED_RECONSTRUCTION_OR_VERIFICATION_FAILED");
});
