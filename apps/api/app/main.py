from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.alerts import AlertManager, NoOpAlertProvider
from app.core.database import SessionLocal
from app.core.metrics import InMemoryMetricCollector, NoOpMetricCollector
from app.core.observability import ObservabilityMiddleware
from app.core.readiness import DefaultReadinessChecker
from app.core.tracing import NoOpTraceProvider, Tracer
from app.core import models_registry  # noqa: F401  (ensures all ORM models are registered)
from app.modules.ai.api.routes import router as ai_router
from app.modules.audit.api.routes import router as audit_router
from app.modules.auth.api.routes import router as auth_router
from app.modules.auth.dependencies import AdminUserDependency
from app.modules.auth.security_store import build_authentication_security_store
from app.modules.audit.middleware import AuditCorrelationMiddleware
from app.modules.chats.api.routes import router as chats_router
from app.modules.cnc.api.routes import router as cnc_router
from app.modules.cad.api.routes import router as cad_router
from app.modules.documents.api.routes import router as documents_router
from app.modules.documents.dependencies import initialize_document_storage
from app.modules.files.api.routes import router as files_router
from app.modules.manufacturing.api.routes import router as manufacturing_router
from app.modules.projects.api.routes import router as projects_router
from app.modules.research.api.routes import router as research_router
from app.modules.users.api.routes import router as users_router

API_VERSION = "1.3.0"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_document_storage()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vena_IA API",
        description="API for intelligent engineering and CNC manufacturing workflows.",
        version=API_VERSION,
        lifespan=lifespan,
    )
    app.state.auth_security_store = build_authentication_security_store(settings)
    app.state.readiness_checker = DefaultReadinessChecker(settings)
    app.state.audit_session_factory = SessionLocal
    app.state.metric_collector = (
        InMemoryMetricCollector()
        if settings.observability_collection_enabled
        else NoOpMetricCollector()
    )
    app.state.alert_manager = AlertManager(
        NoOpAlertProvider(),
        cooldown_seconds=settings.observability_alert_cooldown_seconds,
    )
    app.state.tracer = Tracer(NoOpTraceProvider())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        AuditCorrelationMiddleware,
        session_factory=lambda: app.state.audit_session_factory(),
    )
    app.add_middleware(
        ObservabilityMiddleware,
        application_version=API_VERSION,
        environment=settings.app_env,
        metric_collector=app.state.metric_collector,
        tracer=app.state.tracer,
        alert_manager=app.state.alert_manager,
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "vena-ia-api", "version": API_VERSION}

    @app.get("/ready", tags=["health"])
    def readiness() -> JSONResponse:
        dependencies = app.state.readiness_checker.check()
        ready = all(status == "ready" for status in dependencies.values())
        for dependency, dependency_status in dependencies.items():
            try:
                app.state.metric_collector.set_gauge(
                    "readiness_state",
                    {"dependency": dependency},
                    1 if dependency_status == "ready" else 0,
                )
                if dependency_status != "ready":
                    app.state.metric_collector.increment(
                        "dependency_failures_total", {"dependency": dependency}
                    )
                    app.state.alert_manager.emit(
                        "dependency_unavailable",
                        "critical",
                        context={"dependency": dependency},
                    )
            except Exception:
                pass
        if not ready:
            try:
                app.state.alert_manager.emit("readiness_degraded", "critical")
            except Exception:
                pass
        return JSONResponse(
            status_code=200 if ready else 503,
            content={
                "status": "ready" if ready else "degraded",
                "service": "vena-ia-api",
                "version": API_VERSION,
                "dependencies": dependencies,
            },
        )

    @app.get("/internal/metrics", tags=["operations"])
    def metrics(_admin: AdminUserDependency) -> dict[str, object]:
        if not settings.observability_metrics_endpoint_enabled:
            raise HTTPException(status_code=404, detail="Not found")
        return app.state.metric_collector.snapshot()

    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(files_router)
    app.include_router(chats_router)
    app.include_router(ai_router)
    app.include_router(audit_router)
    app.include_router(documents_router)
    app.include_router(cad_router)
    app.include_router(manufacturing_router)
    app.include_router(cnc_router)
    app.include_router(research_router)

    return app


app = create_app()
