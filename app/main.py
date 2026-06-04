from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router
from utils.config import load_settings
from utils.logging import get_logger, setup_logging
from utils.paths import PROJECT_ROOT


setup_logging()
settings = load_settings()
LOGGER = get_logger(__name__)

app = FastAPI(
    title=settings.get("project.name"),
    version=settings.get("project.version"),
    description="Production-ready AI crypto forecasting API with data ingestion, model training, inference, and quant analytics.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_monitoring(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    LOGGER.info("%s %s -> %s %.2fms", request.method, request.url.path, response.status_code, elapsed_ms)
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.2f}"
    return response


frontend_dir = PROJECT_ROOT / "frontend"
frontend_dist = frontend_dir / "dist"
static_dir = frontend_dist if frontend_dist.exists() else frontend_dir
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    index = Path(frontend_dist / "index.html") if (frontend_dist / "index.html").exists() else Path(frontend_dir / "index.html")
    return FileResponse(index)


app.include_router(router)
