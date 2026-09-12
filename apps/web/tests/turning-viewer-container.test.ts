import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { TurningViewerContainer } from "../components/cam/TurningViewerContainer";
import { cylinderSuccess } from "./fixtures/cylinder-success";
import type { TurningToolpathPlan } from "../lib/turning-contracts";

test("viewer defaults to cylinder fixture with metadata and restricted badges", () => {
  const html = renderToStaticMarkup(createElement(TurningViewerContainer));
  assert.match(html, /value="CYLINDER_SUCCESS" selected=""/);
  assert.match(html, /SUCCESS_SYNTHETIC/);
  assert.match(html, /NON_PRODUCTION/);
  assert.match(html, /PHYSICAL_USE_AUTHORIZED: FALSE/);
  assert.match(html, /G9: PENDENTE/);
  assert.match(html, /MM_PER_REVOLUTION/);
  assert.match(html, /Plano exibido:.*Quantizado/);
  assert.match(html, /<svg/);
  assert.equal((html.match(/<option /g) ?? []).length, 3);
  const plan: TurningToolpathPlan = cylinderSuccess.quantized_plan;
  const moves = plan.operations.reduce((total, operation) => total + operation.moves.length, 0);
  const passes = plan.operations.reduce((total, operation) => total + operation.passes_count, 0);
  assert.equal((html.match(/data-motion=/g) ?? []).length, moves);
  assert.match(html, new RegExp(`Passadas: </dt><dd[^>]*>${passes}</dd>`));
  assert.match(html, new RegExp(`Movimentos: </dt><dd[^>]*>${moves}</dd>`));
});

test("violation selection preserves failure metadata while showing available quantized plan", () => {
  const html = renderToStaticMarkup(createElement(TurningViewerContainer, { initialSelection: "QUANTIZED_VIOLATION" }));
  assert.match(html, /value="QUANTIZED_VIOLATION" selected=""/);
  assert.match(html, /QUANTIZED_BOUNDARY_VIOLATION/);
  assert.match(html, /Motivo:/);
  assert.match(html, /data-motion=/);
  assert.match(html, /PHYSICAL_USE_AUTHORIZED: FALSE/);
});

test("reconstruction failure does not silently display the retained nominal plan", () => {
  const html = renderToStaticMarkup(createElement(TurningViewerContainer, { initialSelection: "RECONSTRUCTION_FAILURE" }));
  assert.match(html, /value="RECONSTRUCTION_FAILURE" selected=""/);
  assert.match(html, /QUANTIZED_VERIFICATION_FAILED/);
  assert.match(html, /QUANTIZED_RECONSTRUCTION_OR_VERIFICATION_FAILED/);
  assert.match(html, /Plano quantizado indisponível/);
  assert.match(html, /Não disponível/);
  assert.doesNotMatch(html, /<svg|data-motion=/);
});

test("local STEP state preserves the synthetic viewer and shows the defensive dispatch banner", () => {
  const html = renderToStaticMarkup(createElement(TurningViewerContainer, {
    initialLocalStepFile: { filename: "bracket.STEP", sizeBytes: 2 * 1024 * 1024 },
  }));
  assert.match(html, /Envio local de arquivo STEP/);
  assert.match(html, /Arquivo local carregado — Pipeline de geometria analítica aguardando despacho\./);
  assert.match(html, /bracket\.STEP.*2\.0 MB/);
  assert.match(html, /Emissão de G-code e despacho físico permanecem bloqueados\./);
  assert.match(html, /value="CYLINDER_SUCCESS" selected=""/);
  assert.match(html, /<svg/);
});
