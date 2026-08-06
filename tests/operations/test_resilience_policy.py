import json
from pathlib import Path

from scripts.resilience_policy import load_policy, validate_policy, validate_repository

ROOT = Path(__file__).resolve().parents[2]


def test_repository_resilience_policy_is_aligned() -> None:
    assert validate_repository(ROOT) == []


def test_policy_rejects_unbounded_attempts_and_sensitive_fields(tmp_path: Path) -> None:
    policy = load_policy(ROOT / "resilience-policy.json")
    policy["operations"][0]["max_attempts"] = 0
    policy["operations"][0]["token"] = "secret"
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    errors = validate_policy(load_policy(path))
    assert any("max_attempts" in error for error in errors)
    assert any("prohibited" in error for error in errors)


def test_policy_has_unique_evidence_backed_operations() -> None:
    policy = load_policy(ROOT / "resilience-policy.json")
    identities = {
        (item["dependency"], item["operation"]) for item in policy["operations"]
    }
    assert len(identities) == len(policy["operations"])
    assert all((ROOT / item["evidence_reference"]).is_file() for item in policy["operations"])
