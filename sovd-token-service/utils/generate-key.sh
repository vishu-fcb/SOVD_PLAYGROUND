#!/bin/bash
# Generate EC P-256 keys for SOVD Token Service

set -e

cd "$(dirname "$0")/.."

KEYS_DIR="keys"
PRIVATE_KEY="$KEYS_DIR/private_key.pem"
PUBLIC_KEY="$KEYS_DIR/public_key.pem"

echo "SOVD Token Service - Key Generation"
echo "===================================="
echo

if ! command -v openssl &> /dev/null; then
    echo "Error: openssl is not installed"
    echo "Please install openssl and try again"
    exit 1
fi

if [ ! -d "$KEYS_DIR" ]; then
    echo "Creating keys directory..."
    mkdir -p "$KEYS_DIR"
fi

if [ -f "$PRIVATE_KEY" ]; then
    echo "Warning: Keys already exist"
    read -p "Overwrite them? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted. Existing keys preserved."
        exit 0
    fi
    echo "Removing existing keys..."
    rm -f "$PRIVATE_KEY" "$PUBLIC_KEY"
fi

echo "Generating EC P-256 private key..."
openssl ecparam -genkey -name prime256v1 -noout -out "$PRIVATE_KEY"

echo "Extracting public key..."
openssl ec -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY" 2>/dev/null

chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"
echo "Set permissions: private (600), public (644)"

echo
echo "Keys generated successfully"
echo "Private key: $PRIVATE_KEY"
echo "Public key:  $PUBLIC_KEY"
echo

echo "Key Information:"
openssl ec -in "$PRIVATE_KEY" -text -noout 2>/dev/null | head -3

echo
echo "Usage:"
echo "- Private key: Token service signs JWTs"
echo "- Public key:  Envoy proxy verifies JWTs"
echo "- Never commit private key to version control"
echo
echo "Done. You can now start the token service."

