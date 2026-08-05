"""Fail-closed checks for the versioned runtime and container policy."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

POLICY_FILE = "runtime-policy.json"
_PINNED_IMAGE = re.compile(r"^[^\s:@]+(?:/[^\s:@]+)*:[^\s@]+@sha256:[0-9a-f]{64}$")
_PINNED_ACTION = re.compile(r"^[^\s@]+@[0-9a-f]{40}$")


def is_pinned_image_reference(reference: str) -> bool:
    """Return whether an OCI reference has a non-floating tag and immutable digest."""
    return bool(_PINNED_IMAGE.fullmatch(reference)) and ":latest@" not in reference.lower()


def _read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _require_contains(
    violations: list[str], *, file_name: str, content: str, expected: str
) -> None:
    if expected not in content:
        violations.append(f"{file_name}: missing required value {expected!r}")


def _load_policy(root: Path) -> dict[str, Any]:
    return json.loads(_read(root, POLICY_FILE))


def validate_repository(root: Path) -> list[str]:
    """Validate repository files against the single versioned runtime manifest."""
    root = root.resolve()
    policy = _load_policy(root)
    violations: list[str] = []

    if policy.get("schema_version") != "vena-ia.runtime-policy/v1":
        violations.append("runtime-policy.json: unsupported schema_version")

    api_docker = _read(root, "apps/api/Dockerfile")
    web_docker = _read(root, "apps/web/Dockerfile")
    compose = _read(root, "docker-compose.yml")
    backend_ci = _read(root, ".github/workflows/backend-ci.yml")
    frontend_ci = _read(root, ".github/workflows/frontend-ci.yml")
    policy_ci = _read(root, ".github/workflows/runtime-policy-ci.yml")
    package = json.loads(_read(root, "apps/web/package.json"))
    lockfile = _read(root, "apps/web/pnpm-lock.yaml")
    pnpm_workspace = _read(root, "apps/web/pnpm-workspace.yaml")

    images = policy.get("images", {})
    expected_locations = {
        "api_base": [("apps/api/Dockerfile", api_docker)],
        "web_base": [("apps/web/Dockerfile", web_docker)],
        "postgres_pgvector": [
            ("docker-compose.yml", compose),
            ("backend-ci.yml", backend_ci),
        ],
        "redis": [("docker-compose.yml", compose), ("backend-ci.yml", backend_ci)],
        "minio": [("docker-compose.yml", compose), ("backend-ci.yml", backend_ci)],
    }
    for name, locations in expected_locations.items():
        reference = images.get(name, "")
        if not is_pinned_image_reference(reference):
            violations.append(f"runtime-policy.json: image {name!r} is not tag+digest pinned")
            continue
        for file_name, content in locations:
            _require_contains(
                violations, file_name=file_name, content=content, expected=reference
            )

    controlled_files = {
        "apps/api/Dockerfile": api_docker,
        "apps/web/Dockerfile": web_docker,
        "docker-compose.yml": compose,
        "backend-ci.yml": backend_ci,
        "runtime-policy-ci.yml": policy_ci,
    }
    for file_name, content in controlled_files.items():
        if re.search(r"(?i):latest(?:\s|@|$)", content):
            violations.append(f"{file_name}: floating latest image is forbidden")

    python = policy["python"]
    node = policy["node"]
    pnpm = policy["pnpm"]
    if _read(root, ".python-version").strip() != python["local_recommended"]:
        violations.append(".python-version diverges from runtime-policy.json")
    if _read(root, ".node-version").strip() != node["local_recommended"]:
        violations.append(".node-version diverges from runtime-policy.json")
    if package.get("packageManager") != f"pnpm@{pnpm['official']}":
        violations.append("apps/web/package.json: packageManager is not pinned")
    if package.get("engines", {}).get("node") != "22.20.x":
        violations.append("apps/web/package.json: Node engine diverges from policy")
    _require_contains(
        violations,
        file_name="apps/web/pnpm-workspace.yaml",
        content=pnpm_workspace,
        expected="onlyBuiltDependencies:\n  - sharp\n  - unrs-resolver",
    )
    if "lockfileVersion: '9.0'" not in lockfile:
        violations.append("apps/web/pnpm-lock.yaml: expected lockfile version 9.0")

    required_values = [
        ("backend-ci.yml", backend_ci, f'python-version: "{python["ci"]}"'),
        ("backend-ci.yml", backend_ci, f"pip=={python['pip']}"),
        ("frontend-ci.yml", frontend_ci, f'node-version: "{node["ci"]}"'),
        ("frontend-ci.yml", frontend_ci, f"pnpm@{pnpm['ci']}"),
        ("frontend-ci.yml", frontend_ci, "pnpm install --frozen-lockfile"),
        ("apps/web/Dockerfile", web_docker, f"pnpm@{pnpm['container']}"),
        ("apps/web/Dockerfile", web_docker, "pnpm install --frozen-lockfile"),
        ("apps/web/Dockerfile", web_docker, "pnpm-workspace.yaml"),
        ("apps/web/Dockerfile", web_docker, 'CMD ["pnpm", "run", "start"]'),
        ("apps/api/Dockerfile", api_docker, "USER vena-ia"),
        ("apps/web/Dockerfile", web_docker, "USER node"),
        ("docker-compose.yml", compose, 'command: ["python", "-m", "scripts.worker"]'),
        ("runtime-policy-ci.yml", policy_ci, "docker build --file apps/api/Dockerfile"),
        ("runtime-policy-ci.yml", policy_ci, "docker build --file apps/web/Dockerfile"),
    ]
    for file_name, content, expected in required_values:
        _require_contains(
            violations, file_name=file_name, content=content, expected=expected
        )

    workflow_text = "\n".join((backend_ci, frontend_ci, policy_ci))
    action_refs = re.findall(r"uses:\s*([^\s#]+)", workflow_text)
    for action_ref in action_refs:
        if not _PINNED_ACTION.fullmatch(action_ref):
            violations.append(f"workflow action is not commit-pinned: {action_ref}")
    for action_ref in policy.get("actions", {}).values():
        if not _PINNED_ACTION.fullmatch(action_ref):
            violations.append(f"runtime-policy.json: invalid action pin {action_ref}")
        if action_ref not in workflow_text:
            violations.append(f"workflow action pin is unused: {action_ref}")

    migration = root / "apps/api/migrations/versions" / (
        f"{policy['migration_head']}_add_asynchronous_jobs.py"
    )
    if not migration.is_file():
        violations.append("runtime-policy.json: migration_head file is missing")

    update_runbook = root / "docs/runbooks/RUNTIME_AND_IMAGE_UPDATES.md"
    if not update_runbook.is_file():
        violations.append("runtime/image update and rollback runbook is missing")
    elif "## Rollback" not in update_runbook.read_text(encoding="utf-8"):
        violations.append("runtime/image runbook does not document rollback")

    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    violations = validate_repository(root)
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}")
        return 1
    print("Runtime policy PASS: versions, images, actions, lockfile and rollback aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
