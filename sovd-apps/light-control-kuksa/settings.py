from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App metadata
    APP_ID: str = "light-control"
    APP_NAME: str = "light-control"
    APP_VERSION: str = "1.0.0"
    APP_VENDOR: str = "DSS"
    APP_DESCRIPTION: str = "SOVD-compliant app that exposes standardized resources"

    # Runtime / Deployment
    APP_URL: str = "http://light-control-kuksa:8085"
    SERVER_URL: str = "http://sovd-server:7690"
    ENABLE_REGISTRATION: bool = False

    # KUKSA Databroker Connection
    KUKSA_IP: str = "127.0.0.1"
    KUKSA_PORT: int = 55555

settings = Settings()
