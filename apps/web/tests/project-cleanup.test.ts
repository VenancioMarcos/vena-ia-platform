import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { runInNewContext } from "node:vm";
import ts from "typescript";

// Execute the actual effect body in a controlled lifecycle, without copying it.
// This tests cancellation semantics; it is not a mounted React integration test.
const source = readFileSync("app/projects/[projectId]/page.tsx", "utf8");
const file = ts.createSourceFile("page.tsx", source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
let effectBody: string | undefined;
function visit(node: ts.Node) {
  if (ts.isCallExpression(node) && node.expression.getText(file) === "useEffect") {
    assert.equal(effectBody, undefined, "Review harness if another effect is introduced");
    effectBody = node.arguments[0].getText(file);
  }
  ts.forEachChild(node, visit);
}
visit(file);
assert.ok(effectBody);
const effectCode = ts.transpileModule(`(${effectBody})()`, {
  compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS },
}).outputText;
function harness() {
  const registry: Record<string, AbortController> = {};
  const ref = { current: registry };
  const signals: AbortSignal[] = [];
  const setup = () => runInNewContext(effectCode, {
    AbortController, jobControllers: ref,
    load: (signal: AbortSignal) => { signals.push(signal); },
  }) as () => void;
  return { registry, ref, signals, setup };
}

test("cleanup cancels initial load and jobs registered after setup", () => {
  const h = harness();
  const cleanup = h.setup();
  h.registry.first = new AbortController();
  h.registry.second = new AbortController();
  assert.equal(h.signals[0].aborted, false);
  cleanup();
  assert.equal(h.signals[0].aborted, true);
  assert.ok(Object.values(h.registry).every(item => item.signal.aborted));
  cleanup(); // Idempotent teardown.
});

test("cleanup retains the registry belonging to its setup", () => {
  const h = harness();
  const cleanup = h.setup();
  h.registry.old = new AbortController();
  const unrelated = new AbortController();
  h.ref.current = { unrelated };
  cleanup();
  assert.equal(h.registry.old.signal.aborted, true);
  assert.equal(unrelated.signal.aborted, false);
});

test("setup-cleanup-setup replay cancels each load and late job independently", () => {
  const h = harness();
  const firstCleanup = h.setup();
  h.registry.job = new AbortController();
  const firstJob = h.registry.job;
  firstCleanup();
  const nextCleanup = h.setup();
  h.registry.job = new AbortController();
  assert.equal(firstJob.signal.aborted, true);
  assert.equal(h.signals[1].aborted, false);
  assert.equal(h.registry.job.signal.aborted, false);
  nextCleanup();
  assert.ok(h.signals.every(signal => signal.aborted));
  assert.equal(h.registry.job.signal.aborted, true);
});
