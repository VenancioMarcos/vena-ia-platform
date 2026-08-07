import { expect, test, type Page, type Route } from "@playwright/test";

const projectId = "11111111-1111-4111-8111-111111111111";
const documentId = "22222222-2222-4222-8222-222222222222";

const workflow = {
  schema_version: "vena-ia.integrated-engineering-workflow/v1",
  workflow_id: "workflow:example",
  source_document: { document_id: documentId, filename: "fixture.step", source_format: "STEP_PART_21" },
  geometry: { schema_version: "vena-ia.geometry-analysis/v1", status: "AVAILABLE", unit: "mm", topology_valid: true, warnings: [], limitations: ["Validated corpus boundary."] },
  features: { schema_version: "vena-ia.geometry-features/v1", status: "AVAILABLE", feature_count: 1, features: [{ feature_id: "feature-0001", feature_type: "THROUGH_CYLINDRICAL_HOLE", confidence_class: "HIGH", review_status: "REQUIRES_HUMAN_REVIEW" }], warnings: [], limitations: ["Conservative recognition."] },
  engineering: { schema_version: "vena-ia.engineering-recommendation/v1", status: "PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW", compatibility: "COMPATIBLE_PRELIMINARY", operation: "DRILLING", preliminary_parameters: { spindle_rpm: { status: "AVAILABLE", value: 1200, unit: "rpm" } }, limitations: ["Catalog values require verification."] },
  planning: { schema_version: "vena-ia.feature-planning/v1", status: "PRELIMINARY", planning_candidates: [{ candidate_type: "DRILLING_CANDIDATE", operation: "DRILLING", status: "PRELIMINARY", executable_output: false }], unavailable_inputs: [], limitations: ["No toolpath."] },
  cnc_neutral_plan: { schema_version: "vena-ia.cnc-neutral-plan/v1", status: "PREVIEW_ONLY", operation: "DRILLING", parameters: { spindle_rpm: 1200 }, warnings: [], limitations: ["No G-code or machine transmission."], review_status: "REQUIRES_HUMAN_REVIEW", simulation_only: true, executable_output: false },
  integrated_report: { schema_version: "vena-ia.integrated-engineering-report/v1", status: "REQUIRES_HUMAN_REVIEW", assumptions: [], missing_inputs: [], limitations: ["Preliminary only."], human_review_checklist: ["Confirm source geometry.", "Confirm catalog versions."], conclusion: "COMPLETE_PRELIMINARY" },
  assumptions: [], missing_inputs: [], limitations: ["NON_PRODUCTION"], warnings: [], traceability: [`document:${documentId}`], review_status: "REQUIRES_HUMAN_REVIEW", workflow_status: "COMPLETE_PRELIMINARY"
} as const;

async function json(route: Route, body: unknown, status = 200) {
  const preflight = route.request().method() === "OPTIONS";
  await route.fulfill({
    status: preflight ? 204 : status,
    contentType: "application/json",
    headers: {
      "Access-Control-Allow-Origin": "http://127.0.0.1:3100",
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    },
    body: preflight ? "" : JSON.stringify(body)
  });
}

async function mockBase(page: Page) {
  await page.route("**/*", (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== "http://localhost:8000") return route.fallback();
    const path = url.pathname;
    if (path === `/projects/${projectId}`) return json(route, { id: projectId, name: "Projeto E2E", status: "ACTIVE" });
    if (path === `/projects/${projectId}/documents`) return json(route, { documents: [{ id: documentId, filename: "fixture.step", status: "UPLOADED" }], total: 1 });
    if (path === `/chat/${projectId}/messages` || path === "/research/reports") return json(route, []);
    if (path === "/engineering/catalogs") return json(route, [
      { id: "material-1", kind: "MATERIAL", code: "STEEL", name: "Steel", data_version: "2026.08", source: "owner supplied" },
      { id: "machine-1", kind: "MACHINE", code: "MILL", name: "Mill", data_version: "2026.08", source: "owner supplied" },
      { id: "tool-1", kind: "TOOL", code: "DRILL", name: "Drill", data_version: "2026.08", source: "owner supplied" }
    ]);
    return json(route, { detail: `Unmocked API path: ${path}` }, 500);
  });
}

async function runWorkflow(page: Page, expectedStatus = "COMPLETE_PRELIMINARY") {
  await page.goto(`/projects/${projectId}`);
  await page.getByRole("combobox", { name: "Documento STEP", exact: true }).selectOption(documentId);
  await page.getByRole("combobox", { name: "Material", exact: true }).selectOption("material-1");
  await page.getByRole("combobox", { name: "Machine", exact: true }).selectOption("machine-1");
  await page.getByRole("combobox", { name: "Tool", exact: true }).selectOption("tool-1");
  const run = page.getByRole("button", { name: "Executar workflow preliminar" });
  await run.focus();
  await expect(run).toBeFocused();
  await run.press("Enter");
  await expect(page.getByText(expectedStatus, { exact: true }).last()).toBeVisible();
}

test.beforeEach(async ({ page }) => {
  await mockBase(page);
});

test("authenticated project renders the deterministic chain, neutral CNC and grounded assistance", async ({ page }) => {
  await page.route("http://localhost:8000/engineering/workflows", (route) => json(route, workflow));
  await page.route("http://localhost:8000/engineering/workflow-assistance", (route) => json(route, {
    schema_version: "vena-ia.specialized-assistance/v1", assistance_id: "assistance:example", profile: "RESEARCH", source_workflow_reference: "workflow:example", source_workflow: workflow,
    evidence_references: ["document:paper:page:3:chunk:chunk-7"], response: "Evidence-based assistance for expert review.", limitations: ["DOE = PRELIMINARY", "ANOVA = DESCRIPTIVE ONLY"], warnings: [], missing_evidence: [],
    citations: [{ document_id: "paper", page_number: 3, chunk_id: "chunk-7", evidence_reference: "document:paper:page:3:chunk:chunk-7", retrieval_method: "COSINE_SIMILARITY", source_quality: "OWNER_PROVIDED", limitations: ["Expert review required."] }],
    review_status: "REQUIRES_HUMAN_REVIEW", assistance_status: "AVAILABLE_FOR_REVIEW", non_production: true, simulation_only: true, executable_output: false, deterministic_input_trace: "sha256:fixture"
  }));
  await runWorkflow(page);
  await expect(page.getByRole("heading", { name: "CAD" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Process Planning" })).toBeVisible();
  await expect(page.getByText("SIMULATION_ONLY").first()).toBeVisible();
  await expect(page.getByText("executable_output=false").first()).toBeVisible();
  await page.getByLabel("REVIEW REQUIRED").check();
  await expect(page.getByText("REVIEW ACKNOWLEDGED")).toBeVisible();
  await page.getByLabel("Perfil").selectOption("RESEARCH");
  await page.getByLabel("Pergunta", { exact: true }).fill("Quais evidências fundamentam este resultado?");
  await page.getByRole("button", { name: "Solicitar assistência para revisão" }).click();
  await expect(page.getByText("AI ASSISTANCE · AVAILABLE_FOR_REVIEW")).toBeVisible();
  await expect(page.getByText(/página 3 · chunk chunk-7/)).toBeVisible();
  await expect(page.getByText("DOE = PRELIMINARY · ANOVA = DESCRIPTIVE ONLY")).toBeVisible();
  await expect(page.getByRole("button", { name: /machine|send|transmit|g-code|m-code/i })).toHaveCount(0);
  const unlabeledControls = await page.locator("main input, main select, main textarea, main button").evaluateAll((controls) =>
    controls.filter((control) => {
      const element = control as HTMLElement;
      if (element.getAttribute("aria-label") || element.getAttribute("aria-labelledby")) return false;
      return !element.closest("label") && !element.textContent?.trim();
    }).length
  );
  expect(unlabeledControls).toBe(0);
});

test("partial workflow exposes missing inputs and unsupported state without infinite loading", async ({ page }) => {
  const partial = { ...workflow, engineering: null, planning: null, cnc_neutral_plan: null, missing_inputs: ["material_id", "machine_id", "tool_id"], warnings: ["Unsupported feature."], workflow_status: "BLOCKED_UNSUPPORTED_FEATURE", integrated_report: { ...workflow.integrated_report, missing_inputs: ["material_id"], conclusion: "BLOCKED_UNSUPPORTED_FEATURE" } };
  await page.route("http://localhost:8000/engineering/workflows", (route) => json(route, partial));
  await runWorkflow(page, "BLOCKED_UNSUPPORTED_FEATURE");
  await expect(page.getByText("BLOCKED_UNSUPPORTED_FEATURE", { exact: true }).last()).toBeVisible();
  await expect(page.getByText("material_id", { exact: true })).toBeVisible();
  await expect(page.getByText("NOT_AVAILABLE", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Executando…")).toHaveCount(0);
});

test("authorization and provider failures fail closed and remain visible", async ({ page }) => {
  await page.route("http://localhost:8000/engineering/workflows", (route) => json(route, { detail: "Document not found" }, 404));
  await page.goto(`/projects/${projectId}`);
  await page.getByRole("combobox", { name: "Documento STEP", exact: true }).selectOption(documentId);
  await page.getByRole("button", { name: "Executar workflow preliminar" }).click();
  await expect(page.getByText("Document not found", { exact: true })).toBeVisible();

  await page.unroute("http://localhost:8000/engineering/workflows");
  await page.route("http://localhost:8000/engineering/workflows", (route) => json(route, workflow));
  await runWorkflow(page);
  await page.route("http://localhost:8000/engineering/workflow-assistance", (route) => json(route, { detail: "Provider unavailable" }, 503));
  await page.getByLabel("Pergunta", { exact: true }).fill("Explain the result");
  await page.getByRole("button", { name: "Solicitar assistência para revisão" }).click();
  await expect(page.getByText("Provider unavailable", { exact: true })).toBeVisible();
  await expect(page.getByText("Consultando…")).toHaveCount(0);
});

test("missing research evidence and blocked unsafe output remain explicit", async ({ page }) => {
  await page.route("http://localhost:8000/engineering/workflows", (route) => json(route, workflow));
  await page.route("http://localhost:8000/engineering/workflow-assistance", (route) => json(route, {
    schema_version: "vena-ia.specialized-assistance/v1", assistance_id: "assistance:blocked", profile: "RESEARCH", source_workflow_reference: "workflow:example", source_workflow: workflow,
    evidence_references: [], response: null, limitations: ["Evidence is required before generation."], warnings: [], missing_evidence: ["research_chunks"], citations: [],
    review_status: "REQUIRES_HUMAN_REVIEW", assistance_status: "BLOCKED_MISSING_EVIDENCE", non_production: true, simulation_only: true, executable_output: false, deterministic_input_trace: "sha256:blocked"
  }));
  await runWorkflow(page);
  await page.getByLabel("Perfil").selectOption("RESEARCH");
  await page.getByLabel("Pergunta", { exact: true }).fill("Summarize the evidence");
  await page.getByRole("button", { name: "Solicitar assistência para revisão" }).click();
  await expect(page.getByText("AI ASSISTANCE · BLOCKED_MISSING_EVIDENCE")).toBeVisible();
  await expect(page.getByText("research_chunks", { exact: true })).toBeVisible();
  await expect(page.getByText("Nenhuma resposta disponível.")).toBeVisible();
});
