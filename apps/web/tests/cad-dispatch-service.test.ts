import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildDispatchFormData,
  dispatchCadJob,
  isTerminalDispatchStatus,
  pollCadDispatchJob,
  type DispatchTransport,
} from "../lib/cad-dispatch-service";

function response(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

test("structures the STEP FormData payload without mutating its bytes", async () => {
  const bytes = new TextEncoder().encode("ISO-10303-21;").buffer;
  const form = buildDispatchFormData({ fileBytes: bytes, filename: "part.step", schema: "AP242" });
  assert.deepEqual([...form.keys()], ["file"]);
  const file = form.get("file");
  assert.ok(file instanceof Blob);
  assert.equal(file.size, bytes.byteLength);
  assert.equal(await file.text(), "ISO-10303-21;");
});

test("preserves queued, processing and completed job transitions", async () => {
  const states = [
    { job_id: "job-42", status: "QUEUED" },
    { job_id: "job-42", status: "PROCESSING" },
    { job_id: "job-42", status: "COMPLETED", profile_data: {
      points: [{ r_mm: 10, z_mm: -20 }, { r_mm: 5, z_mm: 0 }],
      bounding_box: { max_radius_mm: 10, min_z_mm: -20, max_z_mm: 0, total_z_length_mm: 20 },
      review_status: "PROFILE_AVAILABLE_REQUIRES_REVIEW",
      warnings: ["PROFILE_CLOSURE_GAP_WITHIN_TOLERANCE"],
    } },
  ];
  const calls: Array<{ url: string; method: string | undefined }> = [];
  const transport: DispatchTransport = async (input, init) => {
    calls.push({ url: String(input), method: init?.method });
    return response(states.shift());
  };

  const queued = await dispatchCadJob(
    { fileBytes: new Blob(["STEP"]), filename: "part.step", schema: "AP214" },
    { endpoint: "/dispatch", statusEndpoint: "/jobs", transport },
  );
  const processing = await pollCadDispatchJob(queued.jobId, { statusEndpoint: "/jobs", transport });
  const completed = await pollCadDispatchJob(queued.jobId, { statusEndpoint: "/jobs", transport });

  assert.deepEqual([queued.status, processing.status, completed.status], ["QUEUED", "PROCESSING", "COMPLETED"]);
  assert.deepEqual(calls, [
    { url: "/dispatch", method: "POST" },
    { url: "/jobs/job-42", method: "GET" },
    { url: "/jobs/job-42", method: "GET" },
  ]);
  assert.deepEqual(completed.profile, {
    points: [{ radius_mm: 10, z_mm: -20 }, { radius_mm: 5, z_mm: 0 }],
    axis_origin: [0, 0, 0], axis_direction: [0, 0, 1], is_closed: false,
  });
  assert.deepEqual(completed.boundingBox, { maxRadiusMm: 10, minZMm: -20, maxZMm: 0, totalZLengthMm: 20 });
  assert.equal(completed.reviewStatus, "PROFILE_AVAILABLE_REQUIRES_REVIEW");
  assert.deepEqual(completed.warnings, ["PROFILE_CLOSURE_GAP_WITHIN_TOLERANCE"]);
  assert.equal(isTerminalDispatchStatus(queued), false);
  assert.equal(isTerminalDispatchStatus(completed), true);
});

test("uses the integrated backend routes by default", async () => {
  const calls: string[] = [];
  const transport: DispatchTransport = async input => {
    calls.push(String(input));
    return response({ job_id: "job-default", status: "QUEUED" }, 202);
  };
  await dispatchCadJob({ fileBytes: new Blob(["STEP"]), filename: "part.step", schema: "AP242" }, { transport });
  await pollCadDispatchJob("job-default", { transport });
  assert.deepEqual(calls, ["/api/v1/cad/step/dispatch", "/api/v1/cad/step/jobs/job-default"]);
});

test("fails closed when a COMPLETED response has malformed RZ profile data", async () => {
  const invalid = await pollCadDispatchJob("job-bad", { transport: async () => response({
    job_id: "job-bad", status: "COMPLETED", profile_data: {
      points: [{ r_mm: -1, z_mm: 0 }],
      bounding_box: { max_radius_mm: 1, min_z_mm: 0, max_z_mm: 0, total_z_length_mm: 0 },
      review_status: "PROFILE_AVAILABLE_REQUIRES_REVIEW",
    },
  }) });
  assert.deepEqual(invalid, { jobId: "job-bad", status: "FAILED", error: "Perfil RZ retornado pela API é inválido." });
});

test("fails closed when geometry warnings are malformed", async () => {
  const invalid = await pollCadDispatchJob("job-warning", { transport: async () => response({
    job_id: "job-warning", status: "COMPLETED", profile_data: {
      points: [{ r_mm: 1, z_mm: 0 }, { r_mm: 1, z_mm: -1 }],
      bounding_box: { max_radius_mm: 1, min_z_mm: -1, max_z_mm: 0, total_z_length_mm: 1 },
      review_status: "PROFILE_AVAILABLE_REQUIRES_REVIEW",
      warnings: ["VALID", 42],
    },
  }) });
  assert.equal(invalid.status, "FAILED");
});

test("returns a bounded FAILED state for communication errors and invalid responses", async () => {
  const rejected = await dispatchCadJob(
    { fileBytes: new Blob(["STEP"]), filename: "part.step", schema: "AP203" },
    { transport: async () => { throw new Error("private network detail"); } },
  );
  assert.deepEqual(rejected, { jobId: "", status: "FAILED", error: "Falha de comunicação no despacho CAD." });

  const invalid = await pollCadDispatchJob("job-7", { transport: async () => response({ status: "UNKNOWN" }) });
  assert.deepEqual(invalid, { jobId: "job-7", status: "FAILED", error: "Resposta de despacho CAD inválida." });
  assert.equal(isTerminalDispatchStatus(invalid), true);
});

test("aborts a stalled transport at the configured timeout", async () => {
  const transport: DispatchTransport = (_input, init) => new Promise((_resolve, reject) => {
    init?.signal?.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
  });
  const result = await pollCadDispatchJob("job-timeout", { timeoutMs: 5, transport });
  assert.deepEqual(result, {
    jobId: "job-timeout",
    status: "FAILED",
    error: "O despacho CAD excedeu o tempo limite.",
  });
});

test("distinguishes an explicit caller cancellation from a timeout", async () => {
  const controller = new AbortController();
  const transport: DispatchTransport = (_input, init) => new Promise((_resolve, reject) => {
    init?.signal?.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
  });
  const pending = pollCadDispatchJob("job-cancel", { signal: controller.signal, transport });
  controller.abort();
  assert.deepEqual(await pending, {
    jobId: "job-cancel",
    status: "FAILED",
    error: "O despacho CAD foi cancelado.",
  });
});
