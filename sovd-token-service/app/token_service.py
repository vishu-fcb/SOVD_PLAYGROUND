"""Token Service for issuing JWT tokens with specific scopes and actions."""

import time
import uuid
import jwt
from typing import List, Dict, Any
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64


class TokenService:
    """TokenService handles JWT token creation and key management."""

    def __init__(self, key_file: str = "keys/private_key.pem"):
        """Initialize the TokenService with a persistent EC P-256 key pair."""
        self.key_file = Path(key_file)
        
        # Load or generate key
        if self.key_file.exists():
            print(f"Loading existing key from {self.key_file}")
            self._load_key()
        else:
            print(f"Generating new key and saving to {self.key_file}")
            self._generate_and_save_key()
        
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
        
        print(f"✓ Private key saved to {self.key_file}")
    
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
        
        print(f"✓ Private key loaded from {self.key_file}")

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

    def get_public_key_pem(self) -> str:
        """Return the public key in PEM format."""
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode('utf-8')

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
