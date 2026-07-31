from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core import models_registry  # noqa: F401  (ensures all ORM models are registered)
from app.modules.ai.api.routes import router as ai_router
from app.modules.auth.api.routes import router as auth_router
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


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_document_storage()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vena_IA API",
        description="API for intelligent engineering and CNC manufacturing workflows.",
        version="0.9.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "vena-ia-api"}

    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(files_router)
    app.include_router(chats_router)
    app.include_router(ai_router)
    app.include_router(documents_router)
    app.include_router(cad_router)
    app.include_router(manufacturing_router)
    app.include_router(cnc_router)
    app.include_router(research_router)

    return app


app = create_app()
