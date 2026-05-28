# Security Baseline

This project includes backend hardening controls. Keep these operational practices in place:

## Runtime
- Use a strong `SECRET_KEY` (minimum 32 random chars).
- Keep `ACCESS_TOKEN_EXPIRE_MINUTES` short (default 120).
- Enable HTTPS in production (`FORCE_HTTPS=true`) behind TLS.
- Restrict host headers with `TRUSTED_HOSTS`.
- Keep `SECURE_HEADERS_ENABLED=true`.

## Authentication
- Login endpoint uses sliding-window rate limit by IP and username.
- Do not expose detailed auth failure reasons.
- Rotate credentials immediately after incidents.

## Data Validation
- Backend normalizes and validates username, CNPJ, IMEI and phone number.
- Keep server-side validations as source of truth; frontend masks are only UX.

## Backups
- Keep scheduled backups and test restore monthly.
- Store backups encrypted at rest and off-host.
- Windows daily backup helper scripts:
  - `backend/scripts/backup-diario.ps1`
  - `backend/scripts/configurar-backup-diario.ps1`

## Dependency Hygiene
- Update dependencies periodically (`pip list --outdated`, `npm outdated`).
- Run security scans before release (`pip-audit`, `npm audit`).

## Monitoring
- Monitor spikes of HTTP `401`, `403`, `429` and `5xx`.
- Alert on repeated login failures and suspicious report export bursts.
- Monitor `503` responses with message `Banco ocupado` (SQLite lock contention).
- Use `backend/scripts/monitorar-db-lock.ps1` in Scheduler for lock alerts.
- Run monthly checklist with `backend/scripts/healthcheck-mensal.ps1`.

## SQLite Operational Guardrails
- Keep only one backend instance active (`ENFORCE_SINGLE_BACKEND_INSTANCE=true`).
- Avoid running multiple uvicorn workers against the same SQLite file.
