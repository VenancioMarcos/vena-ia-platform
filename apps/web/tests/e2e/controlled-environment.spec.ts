import { expect, test, type Route } from "@playwright/test";

const projectId = "11111111-1111-4111-8111-111111111111";
const documentId = "22222222-2222-4222-8222-222222222222";
const organizationId = "33333333-3333-4333-8333-333333333333";

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

test("controlled environment keeps G9 pending and downloads only a candidate", async ({ page }) => {
  const gates = Array.from({ length: 10 }, (_, index) => ({
    gate: `G${index}`,
    status: index === 9 ? "PENDING_REVIEW" : "PASS",
    evidence_ref: `evidence-${index}`
  }));
  const result = {
    status: "READY_FOR_CONTROLLED_DOWNLOAD",
    classification: "CANDIDATE_FOR_VALIDATION",
    non_production: true,
    review_state: "REQUIRES_HUMAN_REVIEW",
    g9_state: "PENDING_AUTHORITATIVE_REVIEW",
    physical_use_authorized: false,
    machine_send: false,
    dnc: false,
    nc_transfer: false,
    cycle_start: false,
    direct_machine_control: false,
    gcode_candidate: { program: "G21\nG17\nG90\nG94\nM30", output_hash: "a".repeat(64) },
    blind_validation: { gates, replay_hash: "b".repeat(64) },
    digital_thread: {
      thread_id: "thread-controlled",
      organization_id: organizationId,
      status: "COMPLETE_NON_PRODUCTION",
      artifacts: [{ artifact_id: "cad", artifact_type: "CAD", content_hash: "c".repeat(64) }],
      replay_hash: "d".repeat(64),
      g9_state: "PENDING_AUTHORITATIVE_REVIEW",
      physical_use_authorized: false
    },
    download_token: "signed-controlled-download-proof",
    limitations: ["No physical authority."]
  } as const;

  await page.route("**/*", (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== "http://localhost:8000") return route.fallback();
    if (url.pathname === `/projects/${projectId}`) return json(route, { id: projectId, name: "Projeto E2E", status: "ACTIVE" });
    if (url.pathname === `/projects/${projectId}/documents`) return json(route, { documents: [{ id: documentId, filename: "fixture.step", status: "UPLOADED" }], total: 1 });
    if (url.pathname === `/chat/${projectId}/messages` || url.pathname === "/research/reports") return json(route, []);
    if (url.pathname === "/organizations") return json(route, [{ id: organizationId, name: "Controlled E2E", status: "ACTIVE" }]);
    if (url.pathname === "/engineering/catalogs") return json(route, [
      { id: "material-1", kind: "MATERIAL", code: "STEEL", name: "Steel", data_version: "2026.08", source: "owner" },
      { id: "machine-1", kind: "MACHINE", code: "MILL", name: "Mill", data_version: "2026.08", source: "owner" },
      { id: "tool-1", kind: "TOOL", code: "TOOL", name: "Tool", data_version: "2026.08", source: "owner" }
    ]);
    if (url.pathname === "/engineering/controlled-environment/runs") return json(route, result);
    if (url.pathname === "/engineering/controlled-environment/download") return route.fulfill({
      status: 200,
      contentType: "text/plain",
      headers: {
        "Access-Control-Allow-Origin": "http://127.0.0.1:3100",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Expose-Headers": "Content-Disposition",
        "Content-Disposition": 'attachment; filename="fixture.candidate.nc"'
      },
      body: result.gcode_candidate.program
    });
    return json(route, { detail: `Unmocked API path: ${url.pathname}` }, 500);
  });

  await page.goto(`/projects/${projectId}`);
  const controlled = page.getByRole("region", { name: /Ambiente de teste controlado/ });
  await controlled.getByLabel("Organização").selectOption(organizationId);
  await controlled.getByLabel("Documento CAD controlado").selectOption(documentId);
  await controlled.getByLabel("MATERIAL").selectOption("material-1");
  await controlled.getByLabel("MACHINE").selectOption("machine-1");
  await controlled.getByLabel("TOOL").selectOption("tool-1");
  await controlled.getByLabel("Fixture / restrições revisáveis").fill("Synthetic fixture reviewed by a human");
  await controlled.getByLabel("Datum/WCS proposto para confirmação").fill("Z+ datum candidate");
  await controlled.getByLabel("Identificador do holdout selado").fill("holdout-e2e");
  await controlled.getByLabel("SHA-256 da referência selada").fill("f".repeat(64));
  await controlled.getByRole("button", { name: "Executar validação controlada" }).click();

  await expect(page.getByText("G9: PENDING_AUTHORITATIVE_REVIEW")).toBeVisible();
  await expect(page.getByText("PHYSICAL_USE_AUTHORIZED=false")).toBeVisible();
  await expect(page.getByText("G9 · PENDING_REVIEW")).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Download controlado/ }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("fixture.candidate.nc");
  await expect(
    page.getByRole("button", { name: /machine-send|DNC|cycle start|controle direto/i })
  ).toHaveCount(0);
});
