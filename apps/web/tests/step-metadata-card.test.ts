import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { idleDispatchState, reduceCadDispatchState, StepMetadataCard } from "../components/cam/StepMetadataCard";

test("renders supported STEP inspection without physical-emission controls", () => {
  const html = renderToStaticMarkup(createElement(StepMetadataCard, { inspection: { supported: true, metadata: { schema: "AP214", applicationIdentifier: null, lengthUnit: "MILLIMETRE", bytesRead: 1024 }, profile: { source: "STEP_TEXTUAL_METADATA_ONLY", points: [], visualizable: false, limitations: ["NO_GEOMETRY_EXTRACTION", "ASYNC_ANALYSIS_REQUIRED"] } } }));
  assert.match(html, /AP214[\s\S]*MILLIMETRE[\s\S]*1024/);
  assert.match(html, /Inspeção estática local concluída/);
  assert.match(html, /Processar Geometria Analítica/);
  assert.doesNotMatch(html, /G-code|emissão física/i);
});

test("renders the structured unsupported-geometry warning", () => {
  const html = renderToStaticMarkup(createElement(StepMetadataCard, { inspection: { supported: false, reason: "Geometria B-Rep sólida não identificada no cabeçalho textual", metadata: { schema: "UNKNOWN", applicationIdentifier: null, lengthUnit: "UNKNOWN", bytesRead: 32 } } }));
  assert.match(html, /Não identificada/);
  assert.match(html, /Geometria B-Rep sólida não identificada/);
  assert.match(html, /button[^>]*disabled/);
});

test("models dispatch, completion and failure without losing the job identifier", () => {
  const dispatching = reduceCadDispatchState(idleDispatchState, { type: "START" });
  const completed = reduceCadDispatchState(dispatching, { type: "JOB", jobId: "job-ok", status: "COMPLETED" });
  const failed = reduceCadDispatchState(dispatching, { type: "JOB", jobId: "job-fail", status: "FAILED", error: "Falha controlada" });
  assert.deepEqual(dispatching, { phase: "DISPATCHING" });
  assert.deepEqual(completed, { phase: "COMPLETED", jobId: "job-ok" });
  assert.deepEqual(failed, { phase: "FAILED", jobId: "job-fail", error: "Falha controlada" });
});

test("renders active feedback and cancellation, then reducer resets to IDLE", () => {
  const html = renderToStaticMarkup(createElement(StepMetadataCard, {
    inspection: { supported: true, metadata: { schema: "AP242", applicationIdentifier: null, lengthUnit: "MILLIMETRE", bytesRead: 64 }, profile: { source: "STEP_TEXTUAL_METADATA_ONLY", points: [], visualizable: false, limitations: ["NO_GEOMETRY_EXTRACTION", "ASYNC_ANALYSIS_REQUIRED"] } },
    dispatchState: { phase: "DISPATCHING" },
  }));
  assert.match(html, /Enviando análise/);
  assert.match(html, /Cancelar análise/);
  assert.deepEqual(reduceCadDispatchState({ phase: "PROCESSING", jobId: "job-1" }, { type: "RESET" }), { phase: "IDLE" });
});

test("renders completed and failed outcomes without physical-operation controls", () => {
  const inspection = { supported: true as const, metadata: { schema: "AP214" as const, applicationIdentifier: null, lengthUnit: "MILLIMETRE" as const, bytesRead: 128 }, profile: { source: "STEP_TEXTUAL_METADATA_ONLY" as const, points: [] as const, visualizable: false as const, limitations: ["NO_GEOMETRY_EXTRACTION", "ASYNC_ANALYSIS_REQUIRED"] as const } };
  const completed = renderToStaticMarkup(createElement(StepMetadataCard, { inspection, dispatchState: { phase: "COMPLETED", jobId: "job-ok" } }));
  const failed = renderToStaticMarkup(createElement(StepMetadataCard, { inspection, dispatchState: { phase: "FAILED", jobId: "job-bad", error: "Falha controlada" } }));
  assert.match(completed, /Perfil processado e pronto para renderização 2D/);
  assert.match(failed, /Falha controlada/);
  assert.doesNotMatch(completed + failed, /G-code|ciclo de usinagem|emissão física/i);
});
