from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App metadata
    APP_ID: str = "light-control"
    APP_NAME: str = "light-control"
    APP_VERSION: str = "1.0.0"
    APP_VENDOR: str = "DSS"
    APP_DESCRIPTION: str = "SOVD-compliant app that exposes standardized resources"

    # Runtime / Deployment
    APP_URL: str = "http://light-control:8084"
    SERVER_URL: str = "http://sovd-server:7690"

    # Registration
    ENABLE_REGISTRATION: bool = True

settings = Settings()
