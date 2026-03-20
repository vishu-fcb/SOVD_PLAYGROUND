import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path

from sovd.router import sovd_router
from settings import settings
from infrastructure.registration import register_with_server
from sovd.model import diagnostic_app

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",        # always enable Swagger UI
    redoc_url="/redoc",      # always enable ReDoc
    openapi_url="/openapi.json"  # OpenAPI spec JSON
)

# Mount SOVD resources
app.include_router(sovd_router)

@app.get("/ac-dashboard")
def ac_dashboard():
    return FileResponse(BASE_DIR / "static" / "ac_dashboard.html")

@app.on_event("startup")
async def on_startup():
    """Register with central server on startup if enabled and start background worker."""
    if settings.ENABLE_REGISTRATION:
        try:
            await register_with_server(settings.SERVER_URL, settings.APP_URL, app)
        except Exception as e:
            logger.warning(f"Could not register with SOVD server: {e}")

    # Start background worker
    asyncio.create_task(diagnostic_app.start_worker())

@app.get("/")
def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")
