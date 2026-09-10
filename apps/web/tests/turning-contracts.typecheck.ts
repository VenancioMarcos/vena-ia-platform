import type { SyntheticTurningExecutionResult, TurningToolpathPlan } from "../lib/turning-contracts";
import { cylinderSuccess } from "./fixtures/cylinder-success";
import { quantizedViolation } from "./fixtures/quantized-violation";
import { reconstructionFailure } from "./fixtures/reconstruction-failure";

// Compile-time rejection probes; never imported by product code or executed.
function accept(_result: SyntheticTurningExecutionResult): void {}
function rejectionProbes(): void {
  // @ts-expect-error success cannot omit its quantized plan
  accept({ ...cylinderSuccess, quantized_plan: null });
  // @ts-expect-error physical authority cannot be promoted
  accept({ ...cylinderSuccess, physical_use_authorized: true });
  // @ts-expect-error an internal failure cannot fabricate a boundary report
  accept({ ...reconstructionFailure, quantized_verification: quantizedViolation.quantized_verification });
  // @ts-expect-error violation cannot carry a PASS report
  accept({ ...quantizedViolation, quantized_verification: cylinderSuccess.quantized_verification });
  // @ts-expect-error success cannot carry a failure reason
  accept({ ...cylinderSuccess, failure_reason: "invented failure" });
  // @ts-expect-error failure has a fixed reason
  accept({ ...reconstructionFailure, failure_reason: "COLLISION" });
  // @ts-expect-error success must have a quantization digest
  accept({ ...cylinderSuccess, metadata: { ...cylinderSuccess.metadata, quantization_digest_sha256: null } });
  // @ts-expect-error schema version is fixed
  accept({ ...cylinderSuccess, metadata: { ...cylinderSuccess.metadata, schema_version: "synthetic-turning/v2" } });
  // @ts-expect-error status must be one of seven exact values
  accept({ ...cylinderSuccess, pipeline_status: "READY_FOR_MACHINE" });
  // @ts-expect-error failure stage cannot contain quantization artifacts
  accept({ ...cylinderSuccess, pipeline_status: "CAD_EXTRACTION_FAILED", failure_reason: "failed" });
  // @ts-expect-error report violations must contain at least one move index
  accept({ ...quantizedViolation, quantized_verification: { ...quantizedViolation.quantized_verification, violating_moves: [] } });
  const plan: TurningToolpathPlan = cylinderSuccess.plan;
  // @ts-expect-error nested operations are readonly
  plan.operations.push(plan.operations[0]);
}
void rejectionProbes;

// All branches narrow their artifacts; a future status must update this switch.
export function presentStage(result: SyntheticTurningExecutionResult): string {
  switch (result.pipeline_status) {
    case "CAD_EXTRACTION_FAILED": {
      const absent: null = result.profile;
      return `${result.failure_reason}:${absent}`;
    }
    case "PLANNING_FAILED": return `${result.profile.points.length}:${result.failure_reason}`;
    case "BOUNDARY_VERIFICATION_FAILED": return `${result.plan.operations.length}:${result.verification?.boundary_status}`;
    case "QUANTIZATION_FAILED": return result.verification.boundary_status;
    case "QUANTIZED_VERIFICATION_FAILED": {
      const absent: null = result.quantized_plan;
      return `${result.quantization.evaluated_moves_count}:${absent}`;
    }
    case "QUANTIZED_BOUNDARY_VIOLATION": return `${result.quantized_verification.violating_moves[0]}`;
    case "SUCCESS_SYNTHETIC": return `${result.quantized_plan.total_cutting_length_mm}`;
    default: {
      const exhaustive: never = result;
      return exhaustive;
    }
  }
}
