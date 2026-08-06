"""Fail-closed capacity profile and evidence alignment gate."""

from __future__ import annotations

import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.capacity_harness import load_profile, validate_profile


def validate_repository(root: Path) -> list[str]:
    errors = validate_profile(load_profile(root / "capacity-profile.json"))
    required = {
        "scripts/capacity_harness.py": ["vena-ia.capacity-evidence/v1", "run_short_soak"],
        "tests/operations/test_controlled_capacity.py": ["test_controlled_load", "test_short_soak"],
        "docs/runbooks/CONTROLLED_CAPACITY.md": ["vena-ia.capacity-profile/v1"],
        ".github/workflows/controlled-capacity-ci.yml": ["capacity_policy.py"],
        "apps/api/app/core/metrics.py": ["requests_in_flight", "soak_errors_total"],
        "docs/capacity/BOTTLENECK_REPORT.md": ["limite por processo"],
    }
    for relative, markers in required.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing capacity alignment file: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                errors.append(f"{relative}: missing {marker}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Capacity policy PASS: profile, harness, evidence, CI and runbook aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
