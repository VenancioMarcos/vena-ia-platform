"""Real-process, disposable capacity gate for PostgreSQL, Redis and MinIO."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, cast

import httpx
from minio import Minio
from redis import Redis
from sqlalchemy import create_engine, text

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.capacity_harness import build_evidence, load_profile, validate_profile, write_evidence

TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT"}


def synthetic_pdf() -> bytes:
    stream = b"BT /F1 12 Tf 72 720 Td (Controlled capacity evidence for Vena IA.) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, value in enumerate(objects, 1):
        offsets.append(len(payload))
        payload.extend(f"{index} 0 obj\n".encode() + value + b"\nendobj\n")
    xref = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode())
    payload.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(payload)


class Gate:
    def __init__(self, root: Path, profile: dict[str, Any]) -> None:
        self.root = root
        self.profile = profile
        self.apis = ["http://127.0.0.1:8101", "http://127.0.0.1:8102"]
        self.processes: dict[str, subprocess.Popen[bytes]] = {}
        self.logs: list[Any] = []
        self.client = httpx.Client(timeout=15)
        self.redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
        self.engine = create_engine(os.environ["DATABASE_URL"])
        self.minio = Minio(
            os.environ["MINIO_ENDPOINT"],
            access_key=os.environ["MINIO_ACCESS_KEY"],
            secret_key=os.environ["MINIO_SECRET_KEY"],
            secure=False,
        )
        self.latencies: list[float] = []
        self.requests = self.errors = 0
        self.minio_paused = False
        self.claim_consistency_violations = 0

    def start(self, name: str, command: list[str]) -> None:
        log = tempfile.TemporaryFile()
        self.logs.append(log)
        self.processes[name] = subprocess.Popen(
            command,
            cwd=self.root,
            env=os.environ.copy(),
            stdout=log,
            stderr=subprocess.STDOUT,
        )

    def stop(self, name: str) -> None:
        process = self.processes.get(name)
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    def start_topology(self) -> None:
        self.start(
            "api-a",
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--app-dir",
                "apps/api",
                "--host",
                "127.0.0.1",
                "--port",
                "8101",
            ],
        )
        self.start(
            "api-b",
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--app-dir",
                "apps/api",
                "--host",
                "127.0.0.1",
                "--port",
                "8102",
            ],
        )
        self.start("worker-a", [sys.executable, "-m", "scripts.worker"])
        self.start("worker-b", [sys.executable, "-m", "scripts.worker"])
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if all(process.poll() is None for process in self.processes.values()):
                try:
                    states = [self.client.get(f"{url}/ready") for url in self.apis]
                    heartbeats = list(self.redis.scan_iter(match="vena_ia:jobs:worker:heartbeat:*"))
                    if all(item.status_code == 200 for item in states) and len(heartbeats) >= 2:
                        return
                except Exception:
                    pass
            time.sleep(0.25)
        raise RuntimeError("real process topology did not become ready")

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        started = time.perf_counter()
        response = self.client.request(method, url, **kwargs)
        self.latencies.append((time.perf_counter() - started) * 1_000)
        self.requests += 1
        if response.status_code >= 500:
            self.errors += 1
        return response

    @staticmethod
    def require(response: httpx.Response, expected: int | set[int]) -> Any:
        allowed = {expected} if isinstance(expected, int) else expected
        if response.status_code not in allowed:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
        return response.json() if response.content else None

    def queue_snapshot(self) -> dict[str, int]:
        prefix = "vena_ia:jobs"
        lease_ids = cast(list[str], self.redis.zrange(f"{prefix}:leases", 0, -1))
        worker_ids = cast(list[str], self.redis.hkeys(f"{prefix}:workers"))
        if len(lease_ids) != len(set(lease_ids)) or set(lease_ids) != set(worker_ids):
            self.claim_consistency_violations += 1
        return {
            "ready": int(cast(int, self.redis.llen(f"{prefix}:ready"))),
            "delayed": int(cast(int, self.redis.zcard(f"{prefix}:delayed"))),
            "leases": int(cast(int, self.redis.zcard(f"{prefix}:leases"))),
            "scheduled": int(cast(int, self.redis.scard(f"{prefix}:scheduled"))),
        }

    def run(self) -> dict[str, Any]:
        health = [self.require(self.request("GET", f"{url}/health"), 200) for url in self.apis]
        ready = [self.require(self.request("GET", f"{url}/ready"), 200) for url in self.apis]
        credentials = {
            "name": "Capacity Owner",
            "email": "capacity-owner@example.invalid",
            "password": "Capacity-Test-Password-2026!",
        }
        self.require(self.request("POST", f"{self.apis[0]}/auth/register", json=credentials), 201)
        login = self.require(
            self.request(
                "POST",
                f"{self.apis[0]}/auth/login",
                json={"email": credentials["email"], "password": credentials["password"]},
            ),
            200,
        )
        token = login["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        self.require(self.request("GET", f"{self.apis[1]}/auth/me", headers=headers), 200)
        self.require(self.request("GET", f"{self.apis[1]}/projects", headers=headers), 200)
        project = self.require(
            self.request(
                "POST",
                f"{self.apis[0]}/projects",
                headers=headers,
                json={"name": "Disposable capacity project"},
            ),
            201,
        )
        project_id = project["id"]
        self.require(
            self.request("GET", f"{self.apis[1]}/projects/{project_id}", headers=headers), 200
        )

        document_ids: list[str] = []
        job_ids: list[str] = []
        objects_initial = (
            sum(1 for _ in self.minio.list_objects(os.environ["MINIO_BUCKET"], recursive=True))
            if self.minio.bucket_exists(os.environ["MINIO_BUCKET"])
            else 0
        )
        self.stop("worker-a")
        self.stop("worker-b")
        cancel_document = self.require(
            self.request(
                "POST",
                f"{self.apis[0]}/projects/{project_id}/documents",
                headers=headers,
                files={"file": ("cancel.pdf", synthetic_pdf(), "application/pdf")},
            ),
            201,
        )
        document_ids.append(cancel_document["id"])
        cancel_job = self.require(
            self.request(
                "POST",
                f"{self.apis[0]}/documents/{cancel_document['id']}/jobs/processing",
                headers=headers,
                json={"idempotency_key": "capacity-cancel-job"},
            ),
            202,
        )
        cancelled = self.require(
            self.request(
                "POST",
                f"{self.apis[1]}/jobs/{cancel_job['id']}/cancel",
                headers=headers,
            ),
            200,
        )
        if cancelled["status"] != "CANCELLED":
            raise RuntimeError("cross-instance cancellation did not become terminal")
        self.start("worker-a", [sys.executable, "-m", "scripts.worker"])
        self.start("worker-b", [sys.executable, "-m", "scripts.worker"])

        retry_document = self.require(
            self.request(
                "POST",
                f"{self.apis[1]}/projects/{project_id}/documents",
                headers=headers,
                files={"file": ("retry.pdf", b"%PDF-1.7\n%%EOF", "application/pdf")},
            ),
            201,
        )
        document_ids.append(retry_document["id"])
        retry_job = self.require(
            self.request(
                "POST",
                f"{self.apis[1]}/documents/{retry_document['id']}/jobs/processing",
                headers=headers,
                json={"idempotency_key": "capacity-retry-job"},
            ),
            202,
        )
        retry_deadline = time.monotonic() + 20
        first_attempt = None
        while time.monotonic() < retry_deadline:
            candidate = self.require(
                self.request("GET", f"{self.apis[0]}/jobs/{retry_job['id']}", headers=headers),
                200,
            )
            if candidate["status"] == "FAILED":
                first_attempt = candidate["attempt"]
                break
            time.sleep(0.1)
        if first_attempt is None:
            raise RuntimeError("synthetic invalid PDF did not fail safely")
        retried = self.require(
            self.request("POST", f"{self.apis[0]}/jobs/{retry_job['id']}/retry", headers=headers),
            200,
        )
        if retried["status"] != "QUEUED":
            raise RuntimeError("retry endpoint did not requeue the failed job")
        retry_deadline = time.monotonic() + 20
        retry_observed = False
        while time.monotonic() < retry_deadline:
            candidate = self.require(
                self.request("GET", f"{self.apis[1]}/jobs/{retry_job['id']}", headers=headers),
                200,
            )
            if candidate["status"] == "FAILED" and candidate["attempt"] > first_attempt:
                retry_observed = True
                break
            time.sleep(0.1)
        if not retry_observed:
            raise RuntimeError("retried invalid PDF did not reach a safe terminal state")

        queue_initial_components = self.queue_snapshot()
        queue_initial = queue_initial_components["scheduled"]
        queue_peak = queue_initial
        for index in range(self.profile["corpus"]["documents"]):
            upload = self.require(
                self.request(
                    "POST",
                    f"{self.apis[index % 2]}/projects/{project_id}/documents",
                    headers=headers,
                    files={"file": (f"synthetic-{index}.pdf", synthetic_pdf(), "application/pdf")},
                ),
                201,
            )
            document_ids.append(upload["id"])
            job = self.require(
                self.request(
                    "POST",
                    f"{self.apis[(index + 1) % 2]}/documents/{upload['id']}/jobs/processing",
                    headers=headers,
                    json={"idempotency_key": f"capacity-job-{index:02d}"},
                ),
                202,
            )
            repeated = self.require(
                self.request(
                    "POST",
                    f"{self.apis[index % 2]}/documents/{upload['id']}/jobs/processing",
                    headers=headers,
                    json={"idempotency_key": f"capacity-job-{index:02d}"},
                ),
                200,
            )
            if repeated["id"] != job["id"]:
                raise RuntimeError("shared idempotency returned a different job")
            job_ids.append(job["id"])
            queue_peak = max(queue_peak, self.queue_snapshot()["scheduled"])

        minio_failure_safe: bool | str = "NOT_MEASURED"
        minio_recovered: bool | str = "NOT_MEASURED"
        container = os.environ.get("CAPACITY_MINIO_CONTAINER")
        if container:
            subprocess.run(["docker", "pause", container], check=True, timeout=10)
            self.minio_paused = True
            degraded = self.request("GET", f"{self.apis[0]}/ready")
            minio_failure_safe = degraded.status_code == 503
            subprocess.run(["docker", "unpause", container], check=True, timeout=10)
            self.minio_paused = False
            recovery_deadline = time.monotonic() + 20
            while time.monotonic() < recovery_deadline:
                if self.request("GET", f"{self.apis[1]}/ready").status_code == 200:
                    minio_recovered = True
                    break
                time.sleep(0.25)
            if minio_recovered is not True:
                raise RuntimeError("MinIO did not recover after the controlled fault")

        interrupted = False
        recovery_job = job_ids[0]
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            owner = cast(str | None, self.redis.hget("vena_ia:jobs:workers", recovery_job))
            if owner:
                for name in ("worker-a", "worker-b"):
                    process = self.processes[name]
                    if owner.endswith(f"-{process.pid}"):
                        self.stop(name)
                        interrupted = True
                        break
            if interrupted:
                break
            time.sleep(0.02)

        terminal: dict[str, dict[str, Any]] = {}
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline and len(terminal) < len(job_ids):
            for index, job_id in enumerate(job_ids):
                if job_id in terminal:
                    continue
                value = self.require(
                    self.request("GET", f"{self.apis[index % 2]}/jobs/{job_id}", headers=headers),
                    200,
                )
                if value["status"] in TERMINAL:
                    terminal[job_id] = value
            queue_peak = max(queue_peak, self.queue_snapshot()["scheduled"])
            time.sleep(0.1)
        if len(terminal) != len(job_ids) or any(
            item["status"] != "SUCCEEDED" for item in terminal.values()
        ):
            raise RuntimeError("real jobs did not all succeed")
        if interrupted:
            missing = next(
                name for name in ("worker-a", "worker-b") if self.processes[name].poll() is not None
            )
            self.start(missing, [sys.executable, "-m", "scripts.worker"])

        answer = self.require(
            self.request(
                "POST",
                f"{self.apis[1]}/projects/{project_id}/knowledge/ask",
                headers=headers,
                json={"question": "What does the evidence contain?", "limit": 2},
            ),
            200,
        )
        self.require(
            self.request(
                "POST",
                f"{self.apis[0]}/chat/{project_id}/ask",
                headers=headers,
                json={"question": "Summarize the synthetic evidence.", "limit": 2},
            ),
            200,
        )
        report = self.require(
            self.request("GET", f"{self.apis[0]}/chat/{project_id}/messages", headers=headers), 200
        )
        if len(report) != 2:
            raise RuntimeError("grounded report messages were not persisted")

        backpressure_results: list[tuple[int, bool]] = []

        def saturated_call(index: int) -> tuple[int, bool]:
            response = self.request(
                "POST",
                f"{self.apis[index % 2]}/ai/deterministic/chat",
                headers=headers,
                json={"messages": [{"role": "user", "content": "bounded capacity"}]},
            )
            return response.status_code, response.headers.get("Retry-After") == "1"

        with ThreadPoolExecutor(max_workers=8) as executor:
            backpressure_results = list(executor.map(saturated_call, range(16)))
        backpressure_codes = [item[0] for item in backpressure_results]
        if 503 not in backpressure_codes:
            raise RuntimeError("real AI backpressure did not emit 503")
        retry_after_observed = all(
            has_retry_after
            for status_code, has_retry_after in backpressure_results
            if status_code == 503
        )
        recovered_after_saturation = (
            self.request(
                "POST",
                f"{self.apis[0]}/ai/deterministic/chat",
                headers=headers,
                json={"messages": [{"role": "user", "content": "recovery probe"}]},
            ).status_code
            == 200
        )

        soak_started = time.monotonic()
        soak_requests = soak_errors = 0
        while time.monotonic() - soak_started < self.profile["soak"]["duration_seconds"]:
            endpoint = self.apis[soak_requests % 2]
            response = self.request("GET", f"{endpoint}/projects", headers=headers)
            soak_requests += 1
            soak_errors += int(response.status_code != 200)
            time.sleep(0.02)

        other = {
            "name": "Capacity Other",
            "email": "capacity-other@example.invalid",
            "password": credentials["password"],
        }
        self.require(self.request("POST", f"{self.apis[1]}/auth/register", json=other), 201)
        other_login = self.require(
            self.request(
                "POST",
                f"{self.apis[1]}/auth/login",
                json={"email": other["email"], "password": other["password"]},
            ),
            200,
        )
        other_headers = {"Authorization": f"Bearer {other_login['access_token']}"}
        cross_user = self.request(
            "GET", f"{self.apis[0]}/projects/{project_id}", headers=other_headers
        ).status_code
        if cross_user not in {403, 404}:
            raise RuntimeError("cross-user isolation failed")

        objects_before_cleanup = sum(
            1 for _ in self.minio.list_objects(os.environ["MINIO_BUCKET"], recursive=True)
        )
        for index, document_id in enumerate(document_ids):
            self.require(
                self.request(
                    "DELETE",
                    f"{self.apis[index % 2]}/documents/{document_id}",
                    headers=headers,
                ),
                204,
            )

        self.require(self.request("POST", f"{self.apis[0]}/auth/logout", headers=headers), 204)
        revocation_status = self.request(
            "GET", f"{self.apis[1]}/auth/me", headers=headers
        ).status_code
        if revocation_status != 401:
            raise RuntimeError("cross-instance revocation failed")
        rate_codes = []
        for index in range(20):
            response = self.request(
                "POST",
                f"{self.apis[index % 2]}/auth/login",
                json={"email": "rate@example.invalid", "password": "invalid-password"},
            )
            rate_codes.append(response.status_code)
            if response.status_code == 429:
                break
        if 429 not in rate_codes:
            raise RuntimeError("shared Redis rate limit was not observed")

        tracked_job_ids = [cancel_job["id"], retry_job["id"], *job_ids]
        with self.engine.begin() as connection:
            actual_jobs_terminal = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM jobs WHERE id = ANY(:ids) AND status IN ('SUCCEEDED','FAILED','CANCELLED','TIMED_OUT')"
                    ),
                    {"ids": tracked_job_ids},
                ).scalar_one()
            )
            attempts = int(
                connection.execute(
                    text("SELECT COALESCE(max(attempt), 0) FROM jobs WHERE id = ANY(:ids)"),
                    {"ids": tracked_job_ids},
                ).scalar_one()
            )
        queue_final_components = self.queue_snapshot()
        queue_final = queue_final_components["scheduled"]
        non_terminal = len(tracked_job_ids) - actual_jobs_terminal
        heartbeat_count = len(list(self.redis.scan_iter(match="vena_ia:jobs:worker:heartbeat:*")))
        objects_final = sum(
            1 for _ in self.minio.list_objects(os.environ["MINIO_BUCKET"], recursive=True)
        )
        ordered = sorted(self.latencies)
        return {
            "execution_mode": "real-disposable-process-integration",
            "api_processes_started": 2,
            "worker_processes_started": 2,
            "health": [item["status"] for item in health],
            "readiness": [item["status"] for item in ready],
            "requests_completed": self.requests,
            "request_errors_5xx": self.errors,
            "latency_ms": {
                "p50": round(statistics.median(ordered), 3),
                "p95": round(ordered[int((len(ordered) - 1) * 0.95)], 3),
                "p99": round(ordered[int((len(ordered) - 1) * 0.99)], 3),
            },
            "actual_jobs_created": len(tracked_job_ids),
            "actual_jobs_terminal": actual_jobs_terminal,
            "duplicate_claims": self.claim_consistency_violations,
            "max_job_attempt": attempts,
            "queue_initial": queue_initial,
            "queue_initial_components": queue_initial_components,
            "queue_peak": queue_peak,
            "queue_final": queue_final,
            "queue_final_components": queue_final_components,
            "non_terminal_jobs_final": non_terminal,
            "worker_heartbeats_observed": heartbeat_count,
            "worker_interruption_observed": interrupted,
            "lease_recovery_observed": interrupted
            and terminal[recovery_job]["status"] == "SUCCEEDED",
            "shared_redis_auth": True,
            "shared_redis_jobs": True,
            "shared_postgresql": True,
            "shared_minio": True,
            "minio_failure_safe": minio_failure_safe,
            "minio_recovered": minio_recovered,
            "revocation_cross_instance_status": revocation_status,
            "rate_limit_cross_instance_status": 429,
            "idempotency_cross_instance": True,
            "cancellation_cross_instance": cancelled["status"] == "CANCELLED",
            "retry_cross_instance": retry_observed,
            "cross_user_status": cross_user,
            "rag_provider": answer["provider"],
            "report_messages_observed": len(report),
            "backpressure": {
                "successes": backpressure_codes.count(200),
                "service_unavailable": backpressure_codes.count(503),
                "retry_after_observed": retry_after_observed,
                "recovered": recovered_after_saturation,
            },
            "soak": {
                "duration_seconds": round(time.monotonic() - soak_started, 3),
                "requests": soak_requests,
                "errors": soak_errors,
                "postgresql_connections": "NOT_MEASURED",
                "process_memory": "NOT_MEASURED",
                "restarts": 1 if interrupted else 0,
            },
            "minio_objects_created": objects_before_cleanup - objects_initial,
            "minio_objects_cleaned": max(objects_before_cleanup - objects_final, 0),
            "cleanup_result": queue_final == 0
            and non_terminal == 0
            and objects_final == objects_initial,
        }

    def cleanup(self) -> None:
        container = os.environ.get("CAPACITY_MINIO_CONTAINER")
        if container and self.minio_paused:
            subprocess.run(["docker", "unpause", container], check=False, timeout=10)
            self.minio_paused = False
        for name in list(self.processes):
            self.stop(name)
        self.client.close()
        self.engine.dispose()
        for log in self.logs:
            log.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, default=Path("capacity-profile.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default="WORKTREE")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    profile = load_profile(args.profile)
    errors = validate_profile(profile)
    if errors:
        parser.error("; ".join(errors))
    gate = Gate(root, profile)
    try:
        gate.start_topology()
        integrated = gate.run()
        baseline_profile = json.loads(json.dumps(profile))
        baseline_profile["soak"]["duration_seconds"] = 0.1
        evidence = build_evidence(baseline_profile, args.commit)
        evidence["scenario"] = "real-process-controlled-capacity"
        evidence["harness_unit_baseline"] = {
            "load": evidence.pop("load"),
            "soak": evidence.pop("soak"),
            "shared_state": evidence.pop("shared_state"),
        }
        evidence["process_integration_load"] = integrated
        evidence["process_integration_soak"] = integrated["soak"]
        evidence["e2e_cross_instance"] = {
            key: integrated[key]
            for key in (
                "shared_redis_auth",
                "shared_redis_jobs",
                "shared_postgresql",
                "shared_minio",
                "revocation_cross_instance_status",
                "rate_limit_cross_instance_status",
                "idempotency_cross_instance",
                "cancellation_cross_instance",
                "retry_cross_instance",
                "cross_user_status",
            )
        }
        evidence["worker_claims"] = {
            key: integrated[key]
            for key in (
                "actual_jobs_created",
                "actual_jobs_terminal",
                "duplicate_claims",
                "max_job_attempt",
                "worker_heartbeats_observed",
                "lease_recovery_observed",
            )
        }
        evidence["recovery_after_saturation"] = integrated["backpressure"]["recovered"]
        passed = (
            integrated["cleanup_result"]
            and integrated["duplicate_claims"] == 0
            and integrated["actual_jobs_terminal"] == integrated["actual_jobs_created"]
            and integrated["backpressure"]["service_unavailable"] > 0
            and integrated["backpressure"]["retry_after_observed"] is True
            and integrated["minio_failure_safe"] is True
            and integrated["minio_recovered"] is True
            and integrated["lease_recovery_observed"] is True
            and integrated["worker_heartbeats_observed"] >= 2
            and integrated["cancellation_cross_instance"] is True
            and integrated["retry_cross_instance"] is True
            and integrated["soak"]["errors"] == 0
        )
        evidence["guardrail_result"] = "PASS" if passed else "FAIL"
        checksum = write_evidence(evidence, args.output, root)
        print(f"CAPACITY_EVIDENCE_SHA256={checksum}")
        print(f"GUARDRAIL_RESULT={evidence['guardrail_result']}")
        return 0 if passed else 1
    finally:
        gate.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
