"""Generate a safe, deterministic evidence bundle for controlled incident drills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from app.core.alerts import AlertManager, LocalAlertProvider
from app.core.metrics import InMemoryMetricCollector
from app.core.observability import observability_context, structured_event
from app.core.tracing import LocalTraceProvider, Tracer
from scripts.backup_contract import BackupContractError, ensure_outside_repository

DRILL_SCHEMA_VERSION = "vena-ia.incident-drill/v1"
_BUNDLE_NAME = re.compile(r"^vena-ia-incident-drill-[A-Za-z0-9_.-]{1,80}$")
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9_.:/ -]{1,160}$")
_FORBIDDEN_TEXT = re.compile(
    r"authorization|cookie|password|secret|token|api[_ -]?key|user_id|project_id|"
    r"document_id|prompt|embedding|stack trace",
    re.IGNORECASE,
)
ScenarioResult = Literal["pass", "fail"]


class IncidentDrillError(Exception):
    """A drill contract or evidence safety condition was not satisfied."""


@dataclass(frozen=True)
class IncidentScenario:
    scenario: str
    started_at: str
    completed_at: str
    duration_ms: float
    request_id: str
    correlation_id: str
    dependency: str | None
    expected_state: str
    observed_state: str
    alert_code: str
    metric_name: str
    audit_event_type: str | None
    result: ScenarioResult
    limitations: str


@dataclass(frozen=True)
class IncidentDrillReport:
    schema_version: str
    application_version: str
    environment: str
    started_at: str
    completed_at: str
    duration_ms: float
    scenarios: tuple[IncidentScenario, ...]


@dataclass(frozen=True)
class EvidenceBundle:
    report: Path
    checksum: Path
    sha256: str


@dataclass(frozen=True)
class _ScenarioSpec:
    scenario: str
    dependency: str | None
    expected_state: str
    observed_state: str
    alert_code: str
    metric_name: str
    audit_event_type: str | None
    metric_labels: dict[str, str]
    alert_context: dict[str, str]


_SCENARIOS = (
    _ScenarioSpec("postgresql_unavailable_recovered", "postgresql", "unavailable_then_ready", "unavailable_then_ready", "dependency_unavailable", "dependency_failures_total", None, {"dependency": "postgresql"}, {"dependency": "postgresql"}),
    _ScenarioSpec("redis_unavailable_recovered", "redis", "unavailable_then_ready", "unavailable_then_ready", "dependency_unavailable", "dependency_failures_total", None, {"dependency": "redis"}, {"dependency": "redis"}),
    _ScenarioSpec("minio_unavailable_recovered", "minio", "unavailable_then_ready", "unavailable_then_ready", "dependency_unavailable", "dependency_failures_total", None, {"dependency": "minio"}, {"dependency": "minio"}),
    _ScenarioSpec("ai_provider_unavailable", None, "safe_503", "safe_503", "ai_provider_unavailable", "ai_provider_failures_total", None, {"operation": "ai.request"}, {"operation": "ai.request"}),
    _ScenarioSpec("readiness_degraded", None, "safe_503", "safe_503", "readiness_degraded", "readiness_state", None, {"dependency": "redis"}, {}),
    _ScenarioSpec("rate_limit_triggered", None, "safe_429", "safe_429", "rate_limit_threshold", "rate_limits_total", "RATE_LIMIT_EXCEEDED", {"scope": "authentication"}, {"scope": "authentication"}),
    _ScenarioSpec("repeated_authentication_failure", None, "safe_401", "safe_401", "repeated_auth_failure_threshold", "http_requests_total", "LOGIN_FAILURE", {"method": "POST", "route": "/auth/login", "status_class": "4xx"}, {"scope": "authentication"}),
    _ScenarioSpec("document_processing_failure", None, "safe_422", "safe_422", "processing_failure_threshold", "processing_jobs_total", "DOCUMENT_PROCESSING_EXECUTED", {"operation": "document.processing", "outcome": "failed"}, {"operation": "document.processing"}),
    _ScenarioSpec("backup_failure", None, "controlled_failure", "controlled_failure", "backup_job_failed", "processing_jobs_total", None, {"operation": "backup", "outcome": "failed"}, {"operation": "backup"}),
    _ScenarioSpec("restore_failure", None, "controlled_failure", "controlled_failure", "restore_failed", "processing_jobs_total", None, {"operation": "restore", "outcome": "failed"}, {"operation": "restore"}),
    _ScenarioSpec("unexpected_internal_error", None, "safe_500", "safe_500", "unexpected_internal_error", "http_internal_errors_total", None, {"route": "/incident-drill"}, {"route": "/incident-drill", "status_class": "5xx"}),
)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_safe_text(value: str, *, field: str) -> None:
    if not _SAFE_VALUE.fullmatch(value) or _FORBIDDEN_TEXT.search(value):
        raise IncidentDrillError(f"Incident drill {field} is outside the allowlist")


def validate_report(report: IncidentDrillReport) -> None:
    if report.schema_version != DRILL_SCHEMA_VERSION:
        raise IncidentDrillError("Incident drill schema version is unsupported")
    _validate_safe_text(report.application_version, field="application version")
    _validate_safe_text(report.environment, field="environment")
    expected_scenarios = {spec.scenario for spec in _SCENARIOS}
    if {item.scenario for item in report.scenarios} != expected_scenarios:
        raise IncidentDrillError("Incident drill scenario set is incomplete")
    for item in report.scenarios:
        UUID(item.request_id)
        UUID(item.correlation_id)
        for field in (
            item.scenario,
            item.expected_state,
            item.observed_state,
            item.alert_code,
            item.metric_name,
            item.limitations,
        ):
            _validate_safe_text(field, field="evidence value")
        for optional in (item.dependency, item.audit_event_type):
            if optional is not None:
                _validate_safe_text(optional, field="optional evidence value")
        if item.result != "pass" or item.duration_ms < 0:
            raise IncidentDrillError("Incident drill contains a failed or invalid scenario")


def _record_scenario(spec: _ScenarioSpec, started_at: datetime) -> IncidentScenario:
    started = perf_counter()
    request_id = str(uuid5(NAMESPACE_URL, f"vena-ia:{spec.scenario}:request"))
    correlation_id = str(uuid5(NAMESPACE_URL, f"vena-ia:{spec.scenario}:correlation"))
    collector = InMemoryMetricCollector()
    alert_provider = LocalAlertProvider()
    alert_manager = AlertManager(alert_provider, cooldown_seconds=0)
    trace_provider = LocalTraceProvider()
    tracer = Tracer(trace_provider)
    with observability_context(request_id, correlation_id):
        event = structured_event(
            "incident.drill.observed",
            "ERROR",
            dependency=spec.dependency,
            dependency_status=spec.observed_state,
            application_version="1.4.0-dev",
            environment="controlled",
        )
        if spec.metric_name == "readiness_state":
            collector.set_gauge(spec.metric_name, spec.metric_labels, 0)
            collector.set_gauge(spec.metric_name, spec.metric_labels, 1)
        else:
            collector.increment(spec.metric_name, spec.metric_labels)
        alert_manager.emit(
            spec.alert_code,
            "critical" if "failure" in spec.scenario or spec.dependency else "warning",
            context=spec.alert_context,
            correlation_id=correlation_id,
        )
        with tracer.start_span(f"incident.{spec.scenario}") as span:
            span.set_error("controlled_incident")
    snapshot = collector.snapshot()
    series_collection = snapshot.get("series", [])
    series_items = series_collection if isinstance(series_collection, list) else []
    metric_recorded = any(
        isinstance(series, dict) and series.get("name") == spec.metric_name
        for series in series_items
    )
    passed = (
        event.get("request_id") == request_id
        and event.get("correlation_id") == correlation_id
        and metric_recorded
        and len(alert_provider.events) == 1
        and alert_provider.events[0].correlation_id == correlation_id
        and len(trace_provider.spans) == 1
        and trace_provider.spans[0].correlation_id == correlation_id
        and trace_provider.spans[0].status == "error"
    )
    completed_at = started_at
    return IncidentScenario(
        scenario=spec.scenario,
        started_at=_utc(started_at),
        completed_at=_utc(completed_at),
        duration_ms=round((perf_counter() - started) * 1000, 3),
        request_id=request_id,
        correlation_id=correlation_id,
        dependency=spec.dependency,
        expected_state=spec.expected_state,
        observed_state=spec.observed_state,
        alert_code=spec.alert_code,
        metric_name=spec.metric_name,
        audit_event_type=spec.audit_event_type,
        result="pass" if passed else "fail",
        limitations="controlled_disposable_double_no_external_transport",
    )


def run_controlled_drill(
    *,
    application_version: str = "1.4.0-dev",
    environment: str = "controlled-test",
    now: datetime | None = None,
) -> IncidentDrillReport:
    started_at = now or datetime.now(timezone.utc)
    started = perf_counter()
    scenarios = tuple(_record_scenario(spec, started_at) for spec in _SCENARIOS)
    report = IncidentDrillReport(
        schema_version=DRILL_SCHEMA_VERSION,
        application_version=application_version,
        environment=environment,
        started_at=_utc(started_at),
        completed_at=_utc(started_at),
        duration_ms=round((perf_counter() - started) * 1000, 3),
        scenarios=scenarios,
    )
    validate_report(report)
    return report


def deterministic_json(report: IncidentDrillReport) -> bytes:
    validate_report(report)
    return (json.dumps(asdict(report), sort_keys=True, separators=(",", ":")) + "\n").encode()


def _reject_symlink_components(path: Path) -> None:
    absolute = path.absolute()
    for candidate in (absolute, *absolute.parents):
        if candidate.exists() and candidate.is_symlink():
            raise IncidentDrillError("Symlinks are forbidden for incident evidence")


def write_evidence_bundle(
    report: IncidentDrillReport,
    output_directory: Path,
    *,
    bundle_name: str = "vena-ia-incident-drill-evidence",
) -> EvidenceBundle:
    if not _BUNDLE_NAME.fullmatch(bundle_name) or Path(bundle_name).name != bundle_name:
        raise IncidentDrillError("Incident evidence bundle name is unsafe")
    _reject_symlink_components(output_directory)
    try:
        output = ensure_outside_repository(output_directory)
    except BackupContractError as exc:
        raise IncidentDrillError(str(exc)) from exc
    output.mkdir(parents=True, exist_ok=True)
    _reject_symlink_components(output)
    report_path = output / f"{bundle_name}.json"
    checksum_path = output / f"{bundle_name}.sha256"
    temporary_report = output / f".{bundle_name}.json.tmp"
    temporary_checksum = output / f".{bundle_name}.sha256.tmp"
    if any(path.exists() for path in (report_path, checksum_path, temporary_report, temporary_checksum)):
        raise IncidentDrillError("Incident evidence exists; refusing overwrite")
    payload = deterministic_json(report)
    digest = hashlib.sha256(payload).hexdigest()
    created: list[Path] = []
    try:
        temporary_report.write_bytes(payload)
        created.append(temporary_report)
        temporary_checksum.write_text(f"{digest}  {report_path.name}\n", encoding="ascii")
        created.append(temporary_checksum)
        temporary_report.replace(report_path)
        created.append(report_path)
        temporary_checksum.replace(checksum_path)
        created.append(checksum_path)
    except OSError as exc:
        for path in reversed(created):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise IncidentDrillError("Incident evidence bundle could not be written") from exc
    return EvidenceBundle(report_path, checksum_path, digest)


def verify_evidence_bundle(report_path: Path, checksum_path: Path) -> IncidentDrillReport:
    _reject_symlink_components(report_path)
    _reject_symlink_components(checksum_path)
    try:
        safe_report = ensure_outside_repository(report_path)
        safe_checksum = ensure_outside_repository(checksum_path)
        payload = safe_report.read_bytes()
        checksum_line = safe_checksum.read_text(encoding="ascii").strip()
    except (BackupContractError, OSError, UnicodeError) as exc:
        raise IncidentDrillError("Incident evidence bundle is unavailable or unsafe") from exc
    expected_line = f"{hashlib.sha256(payload).hexdigest()}  {safe_report.name}"
    if checksum_line != expected_line:
        raise IncidentDrillError("Incident evidence checksum is invalid")
    try:
        raw = json.loads(payload)
        scenario_payloads = raw.pop("scenarios")
        report = IncidentDrillReport(
            **raw,
            scenarios=tuple(IncidentScenario(**item) for item in scenario_payloads),
        )
        validate_report(report)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise IncidentDrillError("Incident evidence contract is invalid") from exc
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--application-version", default="1.4.0-dev")
    parser.add_argument("--environment", default="controlled-test")
    args = parser.parse_args()
    try:
        report = run_controlled_drill(
            application_version=args.application_version,
            environment=args.environment,
        )
        bundle = write_evidence_bundle(report, args.output_directory)
    except IncidentDrillError as exc:
        parser.error(str(exc))
    print(f"result=pass scenarios={len(report.scenarios)}")
    print(f"evidence={bundle.report.name}")
    print(f"sha256={bundle.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
