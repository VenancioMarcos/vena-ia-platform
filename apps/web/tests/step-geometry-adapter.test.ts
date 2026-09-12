import assert from "node:assert/strict";
import { test } from "node:test";
import { inspectStepGeometry, type StepGeometryFileLike } from "../lib/step-geometry-adapter";

function step(content: string): StepGeometryFileLike {
  return { name: "part.step", size: content.length, slice: () => ({ text: async () => content }) };
}

test("extracts AP203 and AP214 schema metadata from bounded STEP text", async () => {
  const ap203 = await inspectStepGeometry(step("ISO-10303-21; HEADER; FILE_SCHEMA(('AP203')); MANIFOLD_SOLID_BREP;"));
  const ap214 = await inspectStepGeometry(step("ISO-10303-21; HEADER; FILE_SCHEMA(('AP214')); CLOSED_SHELL;"));
  assert.equal(ap203.metadata.schema, "AP203");
  assert.equal(ap214.metadata.schema, "AP214");
  assert.equal(ap203.supported, true);
});

test("detects millimetres from SI unit text", async () => {
  const result = await inspectStepGeometry(step("FILE_SCHEMA(('AP242')); SI_UNIT(.MILLI.,.METRE.); ADVANCED_FACE;"));
  assert.equal(result.metadata.schema, "AP242");
  assert.equal(result.metadata.lengthUnit, "MILLIMETRE");
});

test("rejects payloads without recognized solid B-Rep entities", async () => {
  const result = await inspectStepGeometry(step("ISO-10303-21; HEADER; FILE_SCHEMA(('AP214')); SI_UNIT(.MILLI.,.METRE.);"));
  assert.deepEqual(result, {
    supported: false,
    reason: "Geometria B-Rep sólida não identificada no cabeçalho textual",
    metadata: { schema: "AP214", applicationIdentifier: null, lengthUnit: "MILLIMETRE", bytesRead: 71 },
  });
});
