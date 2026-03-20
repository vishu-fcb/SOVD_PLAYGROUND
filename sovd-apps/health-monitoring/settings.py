from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App metadata
    APP_ID: str = "health-monitoring"
    APP_NAME: str = "health-monitoring"
    APP_VERSION: str = "1.0.1"
    APP_VENDOR: str = "DSS"
    APP_DESCRIPTION: str = "SOVD-compliant app that exposes standardized resources"

    # Runtime / Deployment
    APP_URL: str = "http://health-monitoring:8083"
    SERVER_URL: str = "http://sovd-server:7690"

    # Registration
    ENABLE_REGISTRATION: bool = True

settings = Settings()
