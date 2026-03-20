import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from sovd.router import sovd_router
from infrastructure.registration import register_with_server
from settings import settings

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(sovd_router)


@app.on_event("startup")
async def on_startup():
    # Register with central server on startup if enabled
    if settings.ENABLE_REGISTRATION:
        try:
            await register_with_server(settings.SERVER_URL, settings.APP_URL, app)
        except Exception as e:
            logger.warning(f"Could not register with SOVD server: {e}")


@app.get("/")
def root():
    # Redirect root to API documentation
    return RedirectResponse(url="/docs")
