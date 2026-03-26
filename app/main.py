import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes.views import router as views_router
from app.db import init_db
from app.routes.habits import router as habits_router
from app.routes.checks import router as checks_router


def create_app() -> FastAPI:
    app = FastAPI(title="topuria habits")

    # Templates Jinja2 (render server-side, compatible con HTMX)
    templates = Jinja2Templates(directory="app/templates")
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(views_router)
    app.include_router(habits_router)
    app.include_router(checks_router)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    # Si no existe una ruta, lo resolvemos desde views (default)
    return app


app = create_app()

