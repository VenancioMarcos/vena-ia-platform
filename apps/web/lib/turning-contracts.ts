/** JSON output mirror of Python synthetic-turning/v3. Static types do not
 * validate numeric bounds, finitude, hashes, UTC, geometry or physical safety. */
export type TurningPoint2D = readonly [radius_mm: number, z_mm: number];
export type TurningProfilePoint = Readonly<{ radius_mm: number; z_mm: number }>;
export type TurningProfile2D = Readonly<{
  points: readonly TurningProfilePoint[];
  axis_origin: readonly [number, number, number];
  axis_direction: readonly [number, number, number]; is_closed: boolean;
}>;
export type TurningToolpathMove = Readonly<{
  start_point: TurningPoint2D; end_point: TurningPoint2D;
  motion_type: "RAPID" | "CUTTING" | "RETRACT";
  feed_rate_type: "MM_PER_REVOLUTION" | "MM_PER_MINUTE";
}>;
/** Mission alias: includes RAPID/RETRACT, matching Python TurningToolpathMove. */
export type TurningCutSegment = TurningToolpathMove;
export type TurningOperationPlan = Readonly<{
  operation_id: string; operation_type: "FACING" | "ROUGH_TURNING";
  passes_count: number; moves: readonly TurningToolpathMove[];
}>;
export type TurningToolpathOperation = TurningOperationPlan;
export type TurningToolpathPlan = Readonly<{
  profile_id: string; operations: readonly TurningOperationPlan[];
  total_cutting_length_mm: number; is_collision_free: false;
  collision_status: "NOT_VALIDATED"; executable_output: false; physical_use_authorized: false;
}>;
export type TurningBoundaryViolation = "CHUCK_COLLISION_DETECTED" |
  "CENTERLINE_VIOLATION" | "DECLARED_ZONE_INTERFERENCE";
export type TurningBoundaryStatus = "PASS" | "NOT_EVALUATED" | TurningBoundaryViolation;
type VerificationFlags = Readonly<{
  is_verified: false; collision_status: "NOT_VALIDATED";
  executable_output: false; physical_use_authorized: false;
  limitations: readonly ["NO_STOCK_OR_MATERIAL_REMOVAL_VALIDATION", "NO_REAL_TOOL_OR_FIXTURE_VALIDATION"];
}>;
export type TurningPassedVerification = VerificationFlags & Readonly<{
  boundary_status: "PASS"; declared_boundaries_passed: true; violating_moves: readonly [];
}>;
export type TurningViolatedVerification = VerificationFlags & Readonly<{
  boundary_status: TurningBoundaryViolation; declared_boundaries_passed: false;
  violating_moves: readonly [number, ...number[]];
}>;
export type TurningNotEvaluatedVerification = VerificationFlags & Readonly<{
  boundary_status: "NOT_EVALUATED"; declared_boundaries_passed: false; violating_moves: readonly [];
}>;
export type TurningVerificationReport = TurningPassedVerification |
  TurningViolatedVerification | TurningNotEvaluatedVerification;
/** The backend serializes no separate boundary-report object. */
export type TurningVerificationBoundaryReport = TurningVerificationReport;
export type TurningQuantizationReport = Readonly<{
  original_radius_mm: number; programmed_x_diameter_mm: number;
  reconstructed_radius_mm: number; radial_deviation_mm: number;
  is_boundary_safe: false; boundary_status: "NOT_EVALUATED";
  limitations: readonly ["NUMERICAL_QUANTIZATION_CHECK_ONLY"];
}>;
export type DiameterQuantizationResult = TurningQuantizationReport;
export type TurningPlanQuantizationSummary = Readonly<{
  decimal_places: 1 | 2 | 3 | 4 | 5 | 6; evaluated_moves_count: number;
  max_positive_radial_deviation_mm: number; max_negative_radial_deviation_mm: number;
  /** Two endpoint reports per move, start/end, in global movement order. */
  move_reports: readonly TurningQuantizationReport[];
  is_boundary_safe: false; boundary_status: "NOT_EVALUATED";
  limitations: readonly ["NUMERICAL_QUANTIZATION_AGGREGATE_ONLY"];
}>;
export type PlanDiameterQuantizationSummary = TurningPlanQuantizationSummary;
export type SyntheticTurningMetadata = Readonly<{
  schema_version: "synthetic-turning/v3"; evaluated_at_utc: string;
  parameters_digest_sha256: string; quantization_decimal_places: 1 | 2 | 3 | 4 | 5 | 6;
  quantization_digest_sha256: string | null; quantized_verification_digest_sha256: string | null;
  brep_serialization_digest_sha256: string | null;
  brep_serialization_format: "OCCT_BREP_ASCII_V3_NO_TRIANGLES_NO_NORMALS" | null;
  occt_binding_version: string | null;
  limitations: readonly ["NO_CANONICAL_GEOMETRIC_IDENTITY", "NO_DIGITAL_THREAD_INTEGRATION", "NO_PHYSICAL_AUTHORITY"];
}>;
type StageMetadata<Q extends string | null, V extends string | null> =
  SyntheticTurningMetadata & Readonly<{
    quantization_digest_sha256: Q; quantized_verification_digest_sha256: V;
  }>;
type ExtractedMetadata<Q extends string | null, V extends string | null> =
  StageMetadata<Q, V> & Readonly<{
    brep_serialization_digest_sha256: string;
    brep_serialization_format: "OCCT_BREP_ASCII_V3_NO_TRIANGLES_NO_NORMALS";
    occt_binding_version: string;
  }>;
type OutputFlags = Readonly<{
  is_physical_ready: false; physical_use_authorized: false; executable_output: false;
  emission_status: "CONTROLLER_PROFILE_UNRESOLVED";
}>;
type NoQuantization = Readonly<{
  quantization: null; quantized_plan: null; quantized_verification: null;
}>;
type Quantified = Readonly<{
  profile: TurningProfile2D; plan: TurningToolpathPlan;
  verification: TurningPassedVerification; quantization: TurningPlanQuantizationSummary;
}>;
/** All serialized fields required: Python defaults are materialized by model_dump.
 * Readonly is compile-time only; untrusted JSON still requires runtime validation. */
export type SyntheticTurningExecutionResult = OutputFlags & (
  | (NoQuantization & Readonly<{
      pipeline_status: "CAD_EXTRACTION_FAILED"; failure_reason: string;
      profile: null; plan: null; verification: null; metadata: StageMetadata<null, null>;
    }>)
  | (NoQuantization & Readonly<{
      pipeline_status: "PLANNING_FAILED"; failure_reason: string;
      profile: TurningProfile2D; plan: null; verification: null; metadata: ExtractedMetadata<null, null>;
    }>)
  | (NoQuantization & Readonly<{
      pipeline_status: "BOUNDARY_VERIFICATION_FAILED"; failure_reason: string;
      profile: TurningProfile2D; plan: TurningToolpathPlan;
      verification: TurningViolatedVerification | TurningNotEvaluatedVerification | null;
      metadata: ExtractedMetadata<null, null>;
    }>)
  | (NoQuantization & Readonly<{
      pipeline_status: "QUANTIZATION_FAILED"; failure_reason: string;
      profile: TurningProfile2D; plan: TurningToolpathPlan; verification: TurningPassedVerification;
      metadata: ExtractedMetadata<null, null>;
    }>)
  | (Quantified & Readonly<{
      pipeline_status: "QUANTIZED_VERIFICATION_FAILED";
      failure_reason: "QUANTIZED_RECONSTRUCTION_OR_VERIFICATION_FAILED";
      quantized_plan: null; quantized_verification: null; metadata: ExtractedMetadata<string, null>;
    }>)
  | (Quantified & Readonly<{
      pipeline_status: "QUANTIZED_BOUNDARY_VIOLATION"; failure_reason: string;
      quantized_plan: TurningToolpathPlan; quantized_verification: TurningViolatedVerification;
      metadata: ExtractedMetadata<string, string>;
    }>)
  | (Quantified & Readonly<{
      pipeline_status: "SUCCESS_SYNTHETIC"; failure_reason: null;
      quantized_plan: TurningToolpathPlan; quantized_verification: TurningPassedVerification;
      metadata: ExtractedMetadata<string, string>;
    }>)
);
