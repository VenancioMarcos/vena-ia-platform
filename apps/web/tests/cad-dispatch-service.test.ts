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
  assert.equal(form.get("filename"), "part.step");
  assert.equal(form.get("schema"), "AP242");
  const file = form.get("file");
  assert.ok(file instanceof Blob);
  assert.equal(file.size, bytes.byteLength);
  assert.equal(await file.text(), "ISO-10303-21;");
});

test("preserves queued, processing and completed job transitions", async () => {
  const states = [
    { jobId: "job-42", status: "QUEUED" },
    { jobId: "job-42", status: "PROCESSING" },
    { jobId: "job-42", status: "COMPLETED" },
  ];
  const calls: Array<{ url: string; method: string | undefined }> = [];
  const transport: DispatchTransport = async (input, init) => {
    calls.push({ url: String(input), method: init?.method });
    return response(states.shift());
  };

  const queued = await dispatchCadJob(
    { fileBytes: new Blob(["STEP"]), filename: "part.step", schema: "AP214" },
    { endpoint: "/jobs", transport },
  );
  const processing = await pollCadDispatchJob(queued.jobId, { endpoint: "/jobs", transport });
  const completed = await pollCadDispatchJob(queued.jobId, { endpoint: "/jobs", transport });

  assert.deepEqual([queued.status, processing.status, completed.status], ["QUEUED", "PROCESSING", "COMPLETED"]);
  assert.deepEqual(calls, [
    { url: "/jobs", method: "POST" },
    { url: "/jobs/job-42", method: "GET" },
    { url: "/jobs/job-42", method: "GET" },
  ]);
  assert.equal(isTerminalDispatchStatus(queued), false);
  assert.equal(isTerminalDispatchStatus(completed), true);
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
