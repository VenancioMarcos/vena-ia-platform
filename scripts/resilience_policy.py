"""Fail-closed alignment check for the v1.6 resilience policy."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "vena-ia.resilience-policy/v1"
REQUIRED_OPERATION_FIELDS = frozenset(
    {
        "dependency", "operation", "connect_timeout_seconds",
        "read_timeout_seconds", "total_timeout_seconds", "max_attempts",
        "retry_base_seconds", "retry_max_seconds", "jitter_enabled",
        "retryable_error_codes", "concurrency_limit", "queue_limit",
        "recovery_probe_interval_seconds", "failure_mode", "evidence_reference",
    }
)
PROHIBITED_FIELDS = frozenset(
    {"url", "token", "cookie", "password", "secret", "user_id", "project_id",
     "document_id", "job_id", "prompt", "response", "embedding", "content"}
)


def load_policy(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("resilience policy root must be an object")
    return value


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append("unexpected resilience policy schema")
    operations = policy.get("operations")
    if not isinstance(operations, list) or not operations:
        return [*errors, "operations must be a non-empty list"]
    identities: set[tuple[str, str]] = set()
    for index, raw in enumerate(operations):
        if not isinstance(raw, dict):
            errors.append(f"operations[{index}] must be an object")
            continue
        missing = REQUIRED_OPERATION_FIELDS - raw.keys()
        forbidden = PROHIBITED_FIELDS & raw.keys()
        if missing:
            errors.append(f"operations[{index}] missing {sorted(missing)}")
        if forbidden:
            errors.append(f"operations[{index}] contains prohibited {sorted(forbidden)}")
        identity = (str(raw.get("dependency")), str(raw.get("operation")))
        if identity in identities:
            errors.append(f"duplicate operation {identity}")
        identities.add(identity)
        numeric = (
            "connect_timeout_seconds", "read_timeout_seconds", "total_timeout_seconds",
            "retry_base_seconds", "retry_max_seconds", "concurrency_limit", "queue_limit",
            "recovery_probe_interval_seconds",
        )
        if any(not isinstance(raw.get(field), (int, float)) or raw[field] < 0 for field in numeric):
            errors.append(f"operations[{index}] contains invalid negative/non-numeric budget")
        attempts = raw.get("max_attempts")
        if not isinstance(attempts, int) or not 1 <= attempts <= 10:
            errors.append(f"operations[{index}] max_attempts outside 1..10")
        if raw.get("retry_max_seconds", 0) < raw.get("retry_base_seconds", 0):
            errors.append(f"operations[{index}] retry maximum below base")
        evidence = raw.get("evidence_reference")
        if not isinstance(evidence, str) or evidence.startswith(("/", "http")) or ".." in evidence:
            errors.append(f"operations[{index}] evidence reference is unsafe")
    serialized = json.dumps(policy).lower()
    if any(f'"{field}":' in serialized for field in PROHIBITED_FIELDS):
        errors.append("policy contains a prohibited field anywhere")
    return errors


def validate_repository(root: Path) -> list[str]:
    policy = load_policy(root / "resilience-policy.json")
    errors = validate_policy(policy)
    expected = {
        "apps/api/app/core/config.py": [
            "ai_total_timeout_seconds", "ai_max_attempts", "ai_retry_max_seconds",
            "ai_concurrency_limit", "jobs_retry_max_seconds", "minio_read_timeout_seconds",
            "postgresql_connect_timeout_seconds",
        ],
        ".env.example": [
            "AI_TOTAL_TIMEOUT_SECONDS=30.0", "AI_MAX_ATTEMPTS=3",
            "AI_RETRY_MAX_SECONDS=2.0", "AI_CONCURRENCY_LIMIT=8",
            "JOBS_RETRY_MAX_SECONDS=300.0", "MINIO_READ_TIMEOUT_SECONDS=10.0",
            "POSTGRESQL_CONNECT_TIMEOUT_SECONDS=5",
        ],
        "packages/ai/providers/openai.py": [
            "execute_with_resilience", "BoundedConcurrencyGate", "Retry-After",
        ],
        "apps/api/app/modules/jobs/worker.py": ["self._retry_max", "self._retry_jitter_ratio"],
        ".github/workflows/runtime-policy-ci.yml": ["python scripts/resilience_policy.py"],
        "apps/web/lib/api.ts": ["retryAfterSeconds", "Retry-After"],
        "docs/runbooks/DEPENDENCY_DEGRADATION.md": [SCHEMA_VERSION],
        "docs/runbooks/RETRIES_AND_TIMEOUTS.md": [SCHEMA_VERSION],
    }
    for relative, needles in expected.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required alignment file: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in content:
                errors.append(f"{relative}: missing alignment marker {needle}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        errors = validate_repository(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Resilience policy FAIL: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Resilience policy PASS: budgets, settings, code and runbooks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
