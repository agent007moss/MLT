# Military Leaders Tool (MLT) Backend

Production-oriented FastAPI backend scaffold with modular monolith layout and defense-in-depth controls.

## Architecture decisions
- **Modular monolith**: each domain under `app/modules/*` with thin routers + service layer.
- **Async-first**: SQLAlchemy async sessions and startup lifecycle initialization.
- **Security controls**: Argon2id hashing, JWT access/refresh with rotation/revocation, OTP flow with retries/expiry, lockouts, strict security headers, RBAC checks, audit hash-chain.
- **Auditability**: immutable append-only events with `prev_hash` chain and verification endpoint.
- **Extensibility**: default dashboard module inventory seeded and user layout persisted server-side.

## API endpoints
Prefix defaults to `/api/v1`:
- `POST /auth/register`
- `GET /auth/verify-email`
- `POST /auth/login`
- `POST /auth/verify-2fa`
- `POST /auth/logout`
- `POST /auth/refresh`
- `GET /auth/me`
- `GET/POST/PATCH/DELETE /settings/cards`
- `GET/PUT /settings/layout`
- `GET /audit/events`
- `GET /audit/verify-chain`
- `GET/POST /personnel`
- `GET/POST /org`

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
cp .env.example .env
uvicorn app.main:app --reload
```

## Tests
```bash
pytest -q
```

## Compliance note
This repository implements strong baseline controls for a development scaffold. Formal government compliance (e.g., FedRAMP/NIST 800-53/STIG) still requires:
- control mapping and SSP evidence,
- hardened infrastructure baselines,
- key management/HSM integration,
- centralized SIEM with retention policies,
- SAST/DAST and pen-test evidence,
- vulnerability and patch governance.
