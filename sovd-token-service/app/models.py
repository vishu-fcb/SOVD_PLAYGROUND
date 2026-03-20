"""Request and response models for the Token Service API."""

from pydantic import BaseModel
from typing import List


class TokenRequest(BaseModel):
    """Request model for token endpoint."""
    vin: str = "WVWZZZ1JZXW000000"
    user_id: str = "user:tech123"
    roles: List[str] = ["Workshop_Tech"]
    actions: List[str] = ["readDTC", "execRoutine"]
    issuer: str = "https://auth.oem.example.com"
    audience: str = "sovd-api"
    expires_in: int = 3600


class TokenResponse(BaseModel):
    """Response model for token endpoint."""
    access_token: str
    token_type: str


class JWKSResponse(BaseModel):
    """Response model for JWKS endpoint."""
    keys: List[dict]


class PublicKeyResponse(BaseModel):
    """Response model for public key endpoint."""
    public_key: str
    format: str
    algorithm: str
