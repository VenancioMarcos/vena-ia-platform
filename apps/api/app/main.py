from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core import models_registry  # noqa: F401  (ensures all ORM models are registered)
from app.modules.ai.api.routes import router as ai_router
from app.modules.chats.api.routes import router as chats_router
from app.modules.files.api.routes import router as files_router
from app.modules.projects.api.routes import router as projects_router
from app.modules.users.api.routes import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vena_IA API",
        description="API for intelligent engineering and CNC manufacturing workflows.",
        version="0.1.0",
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
    app.include_router(projects_router)
    app.include_router(files_router)
    app.include_router(chats_router)
    app.include_router(ai_router)

    return app


app = create_app()
