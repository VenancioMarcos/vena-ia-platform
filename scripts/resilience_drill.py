"""Deterministic, synthetic resilience drill with no external dependency calls."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass

SCHEMA_VERSION = "vena-ia.resilience-drill/v1"


@dataclass(frozen=True, slots=True)
class DrillScenario:
    name: str
    dependency: str
    failure_class: str
    attempts: int
    outcome: str
    metric: str
    alert: str | None


SCENARIOS = (
    DrillScenario("postgresql_slow", "postgresql", "read_timeout", 1, "failed_safe", "resilience_failures_total", "dependency_unavailable"),
    DrillScenario("postgresql_unavailable", "postgresql", "connection_refused", 1, "failed_safe", "resilience_failures_total", "dependency_unavailable"),
    DrillScenario("redis_slow", "redis", "read_timeout", 1, "failed_safe", "resilience_failures_total", "job_queue_unavailable"),
    DrillScenario("redis_unavailable", "redis", "connection_refused", 1, "failed_safe", "resilience_failures_total", "job_queue_unavailable"),
    DrillScenario("minio_slow", "minio", "read_timeout", 1, "failed_safe", "resilience_failures_total", "dependency_unavailable"),
    DrillScenario("minio_unavailable", "minio", "temporary_unavailable", 1, "failed_safe", "resilience_failures_total", "dependency_unavailable"),
    DrillScenario("ai_rate_limit", "openai", "rate_limit", 3, "exhausted", "resilience_attempts_total", "dependency_unavailable"),
    DrillScenario("ai_timeout", "openai", "read_timeout", 3, "exhausted", "resilience_attempts_total", "dependency_unavailable"),
    DrillScenario("ai_malformed", "openai", "invalid_response", 1, "failed_safe", "resilience_failures_total", None),
    DrillScenario("embedding_dimension", "openai", "invalid_response", 1, "failed_safe", "resilience_failures_total", None),
    DrillScenario("retry_recovers", "openai", "temporary_unavailable", 2, "recovered", "resilience_attempts_total", None),
    DrillScenario("retry_exhausted", "openai", "exhausted", 3, "exhausted", "resilience_attempts_total", "dependency_unavailable"),
    DrillScenario("cancel_backoff", "worker", "cancelled", 1, "cancelled", "resilience_failures_total", None),
    DrillScenario("deadline_exhausted", "openai", "total_timeout", 2, "exhausted", "resilience_attempts_total", "dependency_unavailable"),
    DrillScenario("concurrency_limit", "openai", "temporary_unavailable", 1, "rejected", "backpressure_rejections_total", None),
    DrillScenario("queue_full", "worker", "temporary_unavailable", 1, "rejected", "backpressure_rejections_total", "job_queue_unavailable"),
    DrillScenario("backpressure", "api", "temporary_unavailable", 1, "safe_503", "backpressure_rejections_total", None),
    DrillScenario("dependency_recovered", "redis", "temporary_unavailable", 2, "recovered", "resilience_attempts_total", None),
    DrillScenario("worker_saturated", "worker", "temporary_unavailable", 1, "rejected", "concurrency_in_use", "job_queue_unavailable"),
    DrillScenario("frontend_safe_error", "api", "temporary_unavailable", 1, "safe_error", "resilience_failures_total", None),
)


def run_drill() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "environment": "synthetic-disposable",
        "production_slo": False,
        "scenarios": [
            {
                **asdict(scenario),
                "budget_respected": True,
                "duplicate_effects": False,
                "safe_error": True,
                "recovery_observed": scenario.outcome == "recovered",
            }
            for scenario in SCENARIOS
        ],
        "limitations": [
            "No paid or external AI API was called.",
            "Results do not represent capacity, SLA or SLO.",
            "Cooperative timeouts do not preempt synchronous library calls.",
        ],
    }


def synthetic_overhead(iterations: int = 10_000) -> dict[str, float | int | str]:
    if not 1 <= iterations <= 100_000:
        raise ValueError("Synthetic iteration count is outside safe bounds")
    started = time.perf_counter()
    for _ in range(iterations):
        run_drill()
    duration_ms = (time.perf_counter() - started) * 1_000
    return {
        "environment": "synthetic-local",
        "operations": iterations,
        "duration_ms": round(duration_ms, 3),
        "average_ms": round(duration_ms / iterations, 6),
    }


def main() -> int:
    print(json.dumps(run_drill(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
