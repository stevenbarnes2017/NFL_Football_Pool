# Project Instructions

## Project

- This is the SundayPickems NFL football pool application.
- The application uses Flask, SQLAlchemy, and PostgreSQL.
- Production is deployed through GitHub Actions -> Harbor -> GitOps -> ArgoCD.
- There is a separate web application deployment and scheduler deployment.
- APScheduler and background jobs are production-critical.

## Safety

- Never access, modify, query, migrate, reset, or delete the production database.
- Never run `create_db.py`.
- Never run `db.drop_all()` or destructive SQL.
- Never run `flask db upgrade` against production.
- Never use `kubectl`, `argocd`, `ssh`, `psql`, or production credentials unless the user explicitly requests it.
- Never deploy to production automatically.
- Never push directly to `main` without explicit user approval.
- Never modify secrets, credentials, VAPID keys, API keys, or environment variables without explicit approval.
- Never commit secrets or private keys.
- Treat `private_key.pem`, which is currently tracked in the repository, as a security issue to be handled separately.

## Development

- Inspect the existing implementation before modifying code.
- Prefer small, targeted changes over broad refactors.
- Preserve existing behavior unless the requested task requires changing it.
- Consider both the web process and scheduler process when changing scheduled jobs.
- Use SQLAlchemy migrations for schema changes; never recreate the database.
- Do not assume pytest is safe because `test_email.py` may contact an external provider.
- Before running tests or scripts, inspect what they execute.
- Do not make unrelated cleanup changes while fixing a bug.

## Git

- Show the proposed changes or diff before committing when practical.
- Do not push or merge without explicit user approval.
- Keep bug fixes isolated from unrelated refactoring.

## Current Priority

- The highest-priority issue is investigating why users did not receive the Web Push notification when NFL spreads were successfully posted.
- Diagnose the root cause before changing code.
- Do not change notification behavior until the failure path is understood.
