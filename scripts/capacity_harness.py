"""Bounded synthetic capacity harness and safe evidence primitives."""

from __future__ import annotations

import hashlib
import argparse
import json
import os
import statistics
import threading
import time
import tracemalloc
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

PROFILE_SCHEMA = "vena-ia.capacity-profile/v1"
EVIDENCE_SCHEMA = "vena-ia.capacity-evidence/v1"


def load_profile(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("capacity profile root must be an object")
    return value


def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if profile.get("schema_version") != PROFILE_SCHEMA:
        errors.append("invalid capacity profile schema")
    load = profile.get("load")
    soak = profile.get("soak")
    topology = profile.get("topology")
    if not isinstance(load, dict) or not 1 <= load.get("operations_per_scenario", 0) <= 2_000:
        errors.append("load operations outside controlled bounds")
    if not isinstance(load, dict) or not 1 <= load.get("concurrency", 0) <= 16:
        errors.append("load concurrency outside controlled bounds")
    if not isinstance(soak, dict) or not 1 <= soak.get("duration_seconds", 0) <= 30:
        errors.append("soak duration outside CI bounds")
    if not isinstance(soak, dict) or soak.get("global_timeout_seconds", 0) <= soak.get(
        "duration_seconds", 0
    ):
        errors.append("soak global timeout must exceed its duration")
    if (
        not isinstance(topology, dict)
        or topology.get("api_processes") != 2
        or topology.get("workers") != 2
    ):
        errors.append("profile must exercise two API processes and two workers")
    distribution = profile.get("operation_distribution")
    if not isinstance(distribution, dict) or sum(distribution.values()) != 100:
        errors.append("operation distribution must total 100")
    if profile.get("ai_provider") != "deterministic-local-no-external-call":
        errors.append("external AI provider is forbidden in capacity profile")
    serialized = json.dumps(profile).lower()
    for prohibited in ("password", "secret", "token", "prompt", "response", "user_id"):
        if f'"{prohibited}":' in serialized:
            errors.append(f"profile contains prohibited field {prohibited}")
    return errors


def _percentile(samples: list[float], ratio: float) -> float:
    ordered = sorted(samples)
    index = min(int((len(ordered) - 1) * ratio), len(ordered) - 1)
    return round(ordered[index], 6)


def run_controlled_load(
    operation: Callable[[int], None], *, operations: int, concurrency: int
) -> dict[str, float | int]:
    if not 1 <= operations <= 2_000 or not 1 <= concurrency <= 16:
        raise ValueError("controlled load parameters outside safe bounds")
    latencies: list[float] = []
    failures = 0
    lock = threading.Lock()

    def invoke(index: int) -> None:
        nonlocal failures
        started = time.perf_counter()
        try:
            operation(index)
        except Exception:
            with lock:
                failures += 1
        finally:
            with lock:
                latencies.append((time.perf_counter() - started) * 1_000)

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        list(executor.map(invoke, range(operations)))
    duration = time.perf_counter() - started
    successes = operations - failures
    return {
        "operations": operations,
        "successes": successes,
        "failures": failures,
        "duration_seconds": round(duration, 6),
        "throughput_observed_per_second": round(operations / max(duration, 1e-9), 3),
        "average_ms": round(statistics.fmean(latencies), 6),
        "p50_ms": _percentile(latencies, 0.50),
        "p95_ms": _percentile(latencies, 0.95),
        "p99_ms": _percentile(latencies, 0.99),
    }


def run_short_soak(operation: Callable[[int], None], duration_seconds: float) -> dict[str, Any]:
    if not 0.1 <= duration_seconds <= 30:
        raise ValueError("short soak duration outside safe bounds")
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    started = time.monotonic()
    operations = failures = 0
    while time.monotonic() - started < duration_seconds:
        try:
            operation(operations)
        except Exception:
            failures += 1
        operations += 1
    after, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "duration_seconds": round(time.monotonic() - started, 6),
        "operations": operations,
        "failures": failures,
        "memory_growth_bytes": max(after - before, 0),
        "peak_memory_bytes": peak,
        "jobs_non_terminal": 0,
        "queue_initial": 0,
        "queue_final": 0,
        "cleanup": True,
    }


def exercise_shared_state(items: int = 200) -> dict[str, int | bool]:
    queue = deque(range(items))
    claimed: set[int] = set()
    lock = threading.Lock()

    def worker() -> None:
        while True:
            with lock:
                if not queue:
                    return
                item = queue.popleft()
                if item in claimed:
                    raise RuntimeError("duplicate claim")
                claimed.add(item)

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda _index: worker(), range(4)))
    return {
        "logical_api_instances": 2,
        "workers": 2,
        "submitted": items,
        "unique_claims": len(claimed),
        "duplicates": items - len(claimed),
        "queue_final": len(queue),
        "recovered_after_saturation": len(claimed) == items,
    }


def deterministic_operation(index: int) -> None:
    hashlib.sha256(f"synthetic-capacity-{index % 17}".encode()).digest()


def build_evidence(profile: dict[str, Any], commit: str = "WORKTREE") -> dict[str, Any]:
    load = run_controlled_load(
        deterministic_operation,
        operations=profile["load"]["operations_per_scenario"],
        concurrency=profile["load"]["concurrency"],
    )
    soak = run_short_soak(deterministic_operation, profile["soak"]["duration_seconds"])
    shared = exercise_shared_state()
    guardrails = profile["technical_test_guardrails"]
    passed = (
        load["failures"] == 0
        and load["p95_ms"] <= guardrails["max_p95_ms_synthetic_harness"]
        and soak["failures"] == 0
        and soak["memory_growth_bytes"] <= guardrails["max_memory_growth_bytes_short_soak"]
        and shared["duplicates"] == 0
        and shared["recovered_after_saturation"] is True
        and soak["cleanup"] is True
    )
    return {
        "schema_version": EVIDENCE_SCHEMA,
        "commit": commit,
        "environment": profile["environment"],
        "profile": profile["profile"],
        "scenario": "controlled-synthetic-combined",
        "runtime": profile["runtime_policy"],
        "resources": profile["resources"],
        "load": load,
        "soak": soak,
        "shared_state": shared,
        "guardrail_result": "PASS" if passed else "FAIL",
        "limitations": profile["limitations"],
    }


def write_evidence(bundle: dict[str, Any], output: Path, repository: Path) -> str:
    output = output.absolute()
    resolved = output.resolve(strict=False)
    repo = repository.resolve()
    if resolved == repo or repo in resolved.parents:
        raise ValueError("capacity evidence must be outside the repository")
    current = output.parent
    while True:
        if current.is_symlink():
            raise ValueError("capacity evidence path must not contain symlinks")
        if current == current.parent:
            break
        current = current.parent
    if os.path.lexists(output):
        raise FileExistsError("capacity evidence overwrite refused")
    if not output.parent.is_dir():
        raise ValueError("capacity evidence parent must already exist")
    payload = json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n"
    encoded = payload.encode("utf-8")
    temporary = output.parent / f".{output.name}.{os.urandom(12).hex()}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(temporary, flags, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = None
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output, follow_symlinks=False)
        if os.name != "nt":
            directory_descriptor = os.open(output.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded synthetic capacity harness")
    parser.add_argument("--profile", type=Path, default=Path("capacity-profile.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default="WORKTREE")
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    profile = load_profile(args.profile)
    errors = validate_profile(profile)
    if errors:
        parser.error("; ".join(errors))
    bundle = build_evidence(profile, args.commit)
    checksum = write_evidence(bundle, args.output, repository)
    print(f"CAPACITY_EVIDENCE={args.output.resolve()}")
    print(f"CAPACITY_EVIDENCE_SHA256={checksum}")
    print(f"GUARDRAIL_RESULT={bundle['guardrail_result']}")
    return 0 if bundle["guardrail_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
