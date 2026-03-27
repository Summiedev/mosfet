from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import connect_db, close_db
from app.middleware.cors import setup_cors
from app.routers import (
    auth,
    patients,
    scans,
    reports,
    report_generation,
    checklists,
    media,
    templates,
    e2e_test,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="RadFlow API",
    description=(
        "Real-time radiology workflow assistant.\n\n"
        "**Base URL:** `/api/v1`\n\n"
        "**Auth:** All protected routes require `Authorization: Bearer <token>` header.\n\n"
        "**OTP provider:** Interswitch (dev fallback prints code to server console)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

setup_cors(app)

PREFIX = "/api/v1"

# ── Core routers ──────────────────────────────────────────────────────────────
app.include_router(auth.router,              prefix=PREFIX)
app.include_router(patients.router,          prefix=PREFIX)
app.include_router(scans.router,             prefix=PREFIX)
app.include_router(reports.router,           prefix=PREFIX)
app.include_router(report_generation.router, prefix=PREFIX)
app.include_router(checklists.router,        prefix=PREFIX)
app.include_router(media.router,             prefix=PREFIX)
app.include_router(templates.router,         prefix=PREFIX)

# ── Dev-only router (E2E tests) ───────────────────────────────────────────────
app.include_router(e2e_test.router,          prefix=PREFIX)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    return JSONResponse({"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV})


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
    }
