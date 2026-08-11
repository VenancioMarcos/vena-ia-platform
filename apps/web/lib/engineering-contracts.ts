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
  artifacts: Array<{ artifact_id: string; artifact_type: string; content_hash: string }>;
  replay_hash: string;
  g9_state: "PENDING_AUTHORITATIVE_REVIEW";
  physical_use_authorized: false;
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
