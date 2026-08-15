export type WorkflowStatus =
  | "COMPLETE_PRELIMINARY"
  | "PARTIAL"
  | "BLOCKED_MISSING_INPUT"
  | "BLOCKED_UNSUPPORTED_FEATURE"
  | "FAILED";

export type AssistanceProfile =
  | "CAD_ANALYSIS"
  | "MANUFACTURING_ENGINEERING"
  | "RESEARCH"
  | "DOCUMENTATION_REPORTING";

export type ReviewStatus = "REQUIRES_HUMAN_REVIEW";
export type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

export type WorkflowRequest = {
  document_id: string;
  feature_id: string;
  material_id?: string;
  machine_id?: string;
  tool_id?: string;
  manufacturing_intent?: string;
};

export type CatalogItem = {
  id: string;
  kind: "MATERIAL" | "MACHINE" | "TOOL";
  code: string;
  name: string;
  data_version: string;
  source: string;
};

export type GeometryFeature = {
  feature_id: string;
  feature_type: string;
  confidence_class: string;
  review_status: string;
};

export type IntegratedWorkflow = {
  schema_version: "vena-ia.integrated-engineering-workflow/v1";
  workflow_id: string;
  source_document: { document_id: string; filename: string; source_format: string };
  geometry: {
    schema_version: string;
    status: string;
    unit: string;
    topology_valid: boolean | null;
    warnings: string[];
    limitations: string[];
  };
  features: {
    schema_version: string;
    status: string;
    feature_count: number;
    features: GeometryFeature[];
    warnings: string[];
    limitations: string[];
  };
  engineering: {
    schema_version: string;
    status: string;
    compatibility: string;
    operation: string;
    preliminary_parameters: Record<string, JsonValue>;
    limitations: string[];
  } | null;
  planning: {
    schema_version: string;
    status: string;
    planning_candidates: Array<{ candidate_type: string; operation: string; status: string; executable_output: false }>;
    unavailable_inputs: string[];
    limitations: string[];
  } | null;
  cnc_neutral_plan: {
    schema_version: "vena-ia.cnc-neutral-plan/v1";
    status: string;
    operation: string;
    parameters: Record<string, number>;
    warnings: string[];
    limitations: string[];
    review_status: ReviewStatus;
    simulation_only: true;
    executable_output: false;
  } | null;
  integrated_report: {
    schema_version: string;
    status: ReviewStatus;
    assumptions: string[];
    missing_inputs: string[];
    limitations: string[];
    human_review_checklist: string[];
    conclusion: WorkflowStatus;
  };
  assumptions: string[];
  missing_inputs: string[];
  limitations: string[];
  warnings: string[];
  traceability: string[];
  review_status: ReviewStatus;
  workflow_status: WorkflowStatus;
};

export type GroundedCitation = {
  document_id: string;
  page_number: number | null;
  chunk_id: string | null;
  evidence_reference: string;
  retrieval_method: string;
  source_quality: string;
  limitations: string[];
};

export type SpecializedAssistance = {
  schema_version: "vena-ia.specialized-assistance/v1";
  assistance_id: string;
  profile: AssistanceProfile;
  source_workflow_reference: string;
  source_workflow: IntegratedWorkflow;
  evidence_references: string[];
  response: string | null;
  limitations: string[];
  warnings: string[];
  missing_evidence: string[];
  citations: GroundedCitation[];
  review_status: ReviewStatus;
  assistance_status: string;
  non_production: true;
  simulation_only: true;
  executable_output: false;
  deterministic_input_trace: string;
};

export type GateEvidence = { gate: string; status: string; evidence_ref: string };
export type DigitalThreadManifest = {
  thread_id: string;
  organization_id: string;
  status: string;
  artifacts: Array<{
    artifact_id: string;
    artifact_type: string;
    schema_version: string;
    content_hash: string;
    lifecycle_status: "CURRENT";
  }>;
  replay_hash: string;
  g9_state: "PENDING_AUTHORITATIVE_REVIEW";
  physical_use_authorized: false;
};
export type ManufacturingGeometryModel = {
  schema_version: "vena-ia.manufacturing-geometry-model/v1";
  planning_schema_version: "vena-ia.verified-process-plan/v1";
  status: string;
  final_geometry: {
    source_geometry_hash: string;
    topology_evidence_hash: string;
    normalized_unit: string;
    bounds: [number[], number[]];
    topology_valid: boolean;
  };
  stock: { status: string; source_ref: string | null; contains_final_geometry: boolean | null };
  removal_regions: Array<{ region_id: string; region_type: string; status: string }>;
  operation_candidates: Array<{
    candidate_id: string;
    operation_class: string;
    status: string;
    target_region_refs: string[];
    executable_output: false;
  }>;
  verification: {
    status: string;
    coherent: boolean;
    deterministic_replay_hash: string;
    physical_validation: false;
  };
  review_state: string;
  executable_output: false;
};
export type ToolpathCandidate = {
  schema_version: "vena-ia.toolpath-candidate/v1";
  status: "CANDIDATE_FOR_VALIDATION" | "REJECTED" | "REQUIRES_INPUT";
  operation_candidate_id: string;
  target_region_ids: string[];
  segments: Array<{
    segment_id: string;
    primitive: "LINEAR";
    motion: "RAPID_CANDIDATE" | "FEED_CANDIDATE";
    target_region_id: string | null;
  }>;
  verification: { status: string; deterministic_replay_hash: string; physical_validation: false };
  review_state: string;
  executable_output: false;
  production_authority: false;
};
export type Level2Evidence = {
  schema_version: "vena-ia.level2-material-removal-evidence/v1";
  status: "PASS_REQUIRES_HUMAN_REVIEW" | "REJECTED" | "REQUIRES_INPUT";
  replay_hash: string;
  reconstructed_segment_count: number;
  target_coverage: string;
  remaining_material: string;
  gouge_detected: boolean;
  protected_surface_violation: boolean;
  rapid_collision_detected: boolean;
  fixture_collision_detected: boolean | null;
  physical_validation: false;
};
export type G9ReviewPackage = {
  schema_version: "vena-ia.g9-review-package/v1";
  package_id: string;
  package_hash: string;
  candidate_output_hash: string;
  digital_thread_id: string;
  digital_thread_replay_hash: string;
  blind_validation_bundle_hash: string;
  blind_validation_replay_hash: string;
  artifact_hashes: Record<string, string>;
  contract_versions: Record<string, string>;
  component_versions: Record<string, string>;
  gates: GateEvidence[];
  g9_state: "PENDING_AUTHORITATIVE_REVIEW";
  automatic_authority: false;
  physical_use_authorized: false;
  required_external_artifacts: string[];
};
export type ControlledEnvironmentResult = {
  status: "READY_FOR_CONTROLLED_DOWNLOAD";
  classification: "CANDIDATE_FOR_VALIDATION";
  non_production: true;
  review_state: "REQUIRES_HUMAN_REVIEW";
  g9_state: "PENDING_AUTHORITATIVE_REVIEW";
  physical_use_authorized: false;
  machine_send: false;
  dnc: false;
  nc_transfer: false;
  cycle_start: false;
  direct_machine_control: false;
  manufacturing_model: ManufacturingGeometryModel;
  toolpath: ToolpathCandidate;
  level2_evidence: Level2Evidence;
  gcode_candidate: { program: string; output_hash: string };
  blind_validation: {
    gates: GateEvidence[];
    replay_hash: string;
  };
  digital_thread: DigitalThreadManifest;
  g9_review_package: G9ReviewPackage;
  download_token: string;
  limitations: string[];
};
