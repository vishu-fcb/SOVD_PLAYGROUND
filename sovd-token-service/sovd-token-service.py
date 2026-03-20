from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any
import time
import uuid
import jwt
from jose import jwk
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64
import os
from pathlib import Path

# Token Service for issuing JWT tokens with specific scopes and actions

class TokenService:
    """TokenService handles JWT token creation and key management."""

    def __init__(self, key_file: str = "keys/private_key.pem"):
        """Initialize the TokenService with a key from the keys directory."""
        self.key_file = Path(key_file)
        
        # Ensure keys directory exists
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load key (must exist - no automatic generation)
        if not self.key_file.exists():
            raise FileNotFoundError(
                f"Private key file not found: {self.key_file}\n"
                f"Please create a private key file in the keys/ directory.\n"
                f"You can generate one using:\n"
                f"  openssl ecparam -genkey -name prime256v1 -noout -out {self.key_file}"
            )
        
        print(f"Loading private key from {self.key_file}")
        self._load_key()
        
        self.public_jwk = self._generate_public_jwk()
        self.key_id = self.public_jwk['kid']
        self.issuer = "https://auth.oem.example.com"
    
    def _generate_and_save_key(self):
        """Generate a new EC P-256 key pair and save to file."""
        self.private_key = ec.generate_private_key(
            ec.SECP256R1(),
            default_backend()
        )
        self.public_key = self.private_key.public_key()

        self.private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Save to file
        with open(self.key_file, 'wb') as f:
            f.write(self.private_key_pem)
        
        print(f"✓ Key saved to {self.key_file}")
    
    def _load_key(self):
        """Load EC P-256 key pair from file."""
        with open(self.key_file, 'rb') as f:
            self.private_key_pem = f.read()
        
        self.private_key = serialization.load_pem_private_key(
            self.private_key_pem,
            password=None,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        print(f"✓ Key loaded from {self.key_file}")

    def _generate_public_jwk(self) -> Dict[str, Any]:
        """Generate the public JWK from the public key."""
        public_numbers = self.public_key.public_numbers()

        jwk_dict = {
            "kty": "EC",
            "crv": "P-256",
            "x": self._int_to_base64url(public_numbers.x),
            "y": self._int_to_base64url(public_numbers.y),
            "use": "sig",
            "alg": "ES256",
            "kid": "e5a72d3d-e387-4c06-9215-246ce87bf331",
        }

        return jwk_dict

    def _int_to_base64url(self, value: int) -> str:
        """Convert integer to base64url format."""
        byte_data = value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')
        return base64.urlsafe_b64encode(byte_data).rstrip(b'=').decode('ascii')

    def get_jwks(self) -> Dict[str, Any]:
        """Return the JWK Set for the public key."""
        return self.public_jwk

    def create_token(
        self, 
        user_id: str, 
        vin: str, 
        roles: List[str],
        actions: List[str], 
        issuer: str = None,
        audience: str = None,
        expires_in: int = 3600
    ) -> str:
        """Create a JWT token with the specified parameters."""
        now = int(time.time())
        expiration = now + expires_in

        auth_details = [{
            "type": "sovd",
            "resources": [{"vin": vin}],
            "actions": actions
        }]

        payload = {
            "iss": issuer or self.issuer,
            "sub": user_id,
            "aud": audience or "sovd-api",
            "iat": now,
            "exp": expiration,
            "jti": str(uuid.uuid4()),
            "roles": roles,
            "authorization_details": auth_details
        }

        token = jwt.encode(
            payload,
            self.private_key_pem,
            algorithm='ES256',
            headers={"kid": self.key_id}
        )

        return token

app = FastAPI(
    title="Token Service", 
    description="A token service that issues JWT tokens with specific scopes and actions"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

token_service = TokenService()

class Token(BaseModel):
    """Response model for token endpoint."""
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    """Request model for token endpoint."""
    vin: str = "WVWZZZ1JZXW000000"
    user_id: str = "user:tech123"
    roles: List[str] = ["Workshop_Tech"]
    actions: List[str] = ["readDTC", "execRoutine"]
    issuer: str = "https://auth.oem.example.com"
    audience: str = "sovd-api"
    expires_in: int = 3600

@app.post("/token", response_model=Token)
async def token(request: TokenRequest):
    """Issue a new JWT token."""
    token = token_service.create_token(
        user_id=request.user_id,
        vin=request.vin,
        roles=request.roles,
        actions=request.actions,
        issuer=request.issuer,
        audience=request.audience,
        expires_in=request.expires_in
    )

    return {"access_token": token, "token_type": "bearer"}

@app.get("/.well-known/jwks.json")
async def jwks_endpoint():
    """Provide the JSON Web Key Set (JWKS) for token verification."""
    return {"keys": [token_service.get_jwks()]}

@app.get("/api")
async def api_info():
    """API endpoint that provides basic service information."""
    return {"message": "Token Service is running. Use /docs to access the API documentation."}

# Mount static files for the UI
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run("sovd-token-service:app", host="0.0.0.0", port=8000, reload=True)
