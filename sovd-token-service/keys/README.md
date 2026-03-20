# Keys

Private key for JWT signing.

## Generate

```bash
./generate-key.sh
```

Or manually:
```bash
openssl ecparam -genkey -name prime256v1 -noout -out keys/private_key.pem
chmod 600 keys/private_key.pem
```

## Spec

- File: `private_key.pem`
- Algorithm: EC P-256
- Format: PEM
- Permissions: 600

## Production

- Store in secrets management (AWS Secrets Manager, Vault)
- Mount read-only in containers
- Rotate per security policy
- Never commit to git
