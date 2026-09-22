import { mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const tests = readdirSync(join(root, "tests"))
  .filter((name) => name.endsWith(".test.ts"))
  .sort()
  .map((name) => join("tests", name));
const output = mkdtempSync(join(tmpdir(), "vena-ia-web-tests-"));

function run(args) {
  const result = spawnSync(process.execPath, args, {
    cwd: root,
    encoding: "utf8",
    stdio: "inherit",
    env: { ...process.env, NODE_PATH: join(root, "node_modules") }
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`Test command exited with ${result.status ?? 1}`);
}

try {
  run([
    join("node_modules", "typescript", "bin", "tsc"),
    ...tests,
    "--outDir", output,
    "--module", "commonjs",
    "--target", "ES2020",
    "--moduleResolution", "node",
    "--jsx", "react-jsx",
    "--esModuleInterop",
    "--strict",
    "--skipLibCheck",
    "--noEmitOnError",
    "--typeRoots", join("node_modules", "@types"),
    "--types", "node"
  ]);
  const compiled = readdirSync(join(output, "tests"))
    .filter((name) => name.endsWith(".test.js"))
    .sort()
    .map((name) => join(output, "tests", name));
  run(["--test", ...compiled]);
} finally {
  rmSync(output, { recursive: true, force: true });
}
