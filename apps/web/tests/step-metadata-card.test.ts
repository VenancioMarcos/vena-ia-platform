import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { StepMetadataCard } from "../components/cam/StepMetadataCard";

test("renders supported STEP inspection without physical-emission controls", () => {
  const html = renderToStaticMarkup(createElement(StepMetadataCard, { inspection: { supported: true, metadata: { schema: "AP214", applicationIdentifier: null, lengthUnit: "MILLIMETRE", bytesRead: 1024 }, profile: { source: "STEP_TEXTUAL_METADATA_ONLY", points: [], visualizable: false, limitations: ["NO_GEOMETRY_EXTRACTION", "ASYNC_ANALYSIS_REQUIRED"] } } }));
  assert.match(html, /AP214[\s\S]*MILLIMETRE[\s\S]*1024/);
  assert.match(html, /Inspeção estática local concluída/);
  assert.doesNotMatch(html, /button|G-code|emissão física/i);
});

test("renders the structured unsupported-geometry warning", () => {
  const html = renderToStaticMarkup(createElement(StepMetadataCard, { inspection: { supported: false, reason: "Geometria B-Rep sólida não identificada no cabeçalho textual", metadata: { schema: "UNKNOWN", applicationIdentifier: null, lengthUnit: "UNKNOWN", bytesRead: 32 } } }));
  assert.match(html, /Não identificada/);
  assert.match(html, /Geometria B-Rep sólida não identificada/);
});
