from scripts.resilience_drill import SCENARIOS, SCHEMA_VERSION, run_drill, synthetic_overhead


def test_resilience_drill_covers_required_scenarios_safely() -> None:
    report = run_drill()
    assert report["schema_version"] == SCHEMA_VERSION
    assert len(report["scenarios"]) == 20
    assert {item.dependency for item in SCENARIOS} >= {
        "postgresql", "redis", "minio", "openai", "worker", "api"
    }
    assert all(item["budget_respected"] for item in report["scenarios"])
    assert not any(item["duplicate_effects"] for item in report["scenarios"])
    serialized = str(report).lower()
    assert "user_id" not in serialized
    assert "project_id" not in serialized
    assert "document_id" not in serialized


def test_synthetic_overhead_is_bounded_and_not_a_capacity_claim() -> None:
    result = synthetic_overhead(100)
    assert result["operations"] == 100
    assert result["duration_ms"] >= 0
    assert result["p50_ms"] <= result["p99_ms"]
    assert result["p95_ms"] <= result["p99_ms"]
    assert result["environment"] == "synthetic-local"


def test_synthetic_overhead_rejects_unbounded_runs() -> None:
    for invalid in (0, 100_001):
        try:
            synthetic_overhead(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid iteration count was accepted")
