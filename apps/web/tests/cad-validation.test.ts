import assert from "node:assert/strict";
import { test } from "node:test";
import { DEFAULT_STEP_MAX_SIZE_BYTES, validateStepFile, type StepFileLike } from "../lib/cad-validation";

function fixture(name: string, content: string, size = content.length): StepFileLike {
  return { name, size, slice: () => ({ text: async () => content }) };
}

test("accepts a STEP file with an ISO-10303-21 header", async () => {
  const result = await validateStepFile(fixture("part.STEP", "ISO-10303-21;\nHEADER;\nENDSEC;"));
  assert.deepEqual(result, { valid: true, metadata: { filename: "part.STEP", sizeBytes: 29 } });
});

test("rejects invalid extensions and empty files", async () => {
  assert.deepEqual(await validateStepFile(fixture("part.dwg", "ISO-10303-21;\nHEADER;")), {
    valid: false, error: "Use um arquivo com extensão .step ou .stp.",
  });
  assert.deepEqual(await validateStepFile(fixture("empty.stp", "", 0)), {
    valid: false, error: "O arquivo STEP está vazio ou possui tamanho inválido.",
  });
});

test("rejects files that exceed the configured size limit", async () => {
  const result = await validateStepFile(fixture("large.stp", "ISO-10303-21;\nHEADER;", 16), { maxSizeBytes: 15 });
  assert.deepEqual(result, { valid: false, error: "O arquivo excede o limite de 15 bytes." });
  assert.equal(DEFAULT_STEP_MAX_SIZE_BYTES, 15 * 1024 * 1024);
});

test("rejects a non-STEP payload masquerading as a STEP file", async () => {
  const result = await validateStepFile(fixture("payload.step", "<html>not a CAD model</html>"));
  assert.deepEqual(result, { valid: false, error: "O arquivo não possui um cabeçalho ISO-10303-21 STEP válido." });
});
