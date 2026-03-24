from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.migrate import run_migrations
from app.db.pool import create_pool
from app.routers import agent_connections as agent_connections_router
from app.routers import db as db_router
from app.routers import files as files_router
from app.routers import health as health_router
from app.routers import permissions as permissions_router
from app.routers import projects as projects_router
from app.routers import proposal_lifecycle as proposal_lifecycle_router
from app.routers import workspaces as workspaces_router
from app.routers import write as write_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.db_pool = None
    if settings.database_url:
        run_migrations(settings.database_url)
        pool = create_pool(settings.database_url)
        pool.open()
        app.state.db_pool = pool
    try:
        yield
    finally:
        pool = getattr(app.state, "db_pool", None)
        if pool is not None:
            pool.close()


def create_app() -> FastAPI:
    application = FastAPI(title="Piggyback API", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router.router)
    application.include_router(db_router.router)
    application.include_router(workspaces_router.router)
    application.include_router(projects_router.router)
    application.include_router(permissions_router.router)
    application.include_router(files_router.router)
    application.include_router(agent_connections_router.router)
    application.include_router(proposal_lifecycle_router.router)
    application.include_router(write_router.router)
    return application


app = create_app()
