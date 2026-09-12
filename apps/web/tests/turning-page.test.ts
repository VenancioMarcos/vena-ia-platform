import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TurningInspectorPage from "../app/cam/turning/page";

test("sandbox page exposes title, disclaimer and fixture inspector in SSR", () => {
  const html = renderToStaticMarkup(createElement(TurningInspectorPage));
  assert.match(html, /^<main/);
  assert.match(html, /<h1[^>]*>CAM Turning 2D Profile Inspector \(Synthetic Sandbox\)<\/h1>/);
  assert.match(html, /Ambiente de inspeção geométrica sintética 2D\. Operações de usinagem física desautorizadas\./);
  assert.match(html, /aria-label="Inspeção de fixtures de torneamento"/);
  assert.match(html, /value="CYLINDER_SUCCESS" selected=""/);
  assert.match(html, /PHYSICAL_USE_AUTHORIZED: FALSE/);
  assert.match(html, /<svg/);
});
