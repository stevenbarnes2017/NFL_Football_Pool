# Project Instructions

## Project

- This is the SundayPickems NFL football pool application.
- The application uses Flask, SQLAlchemy, and PostgreSQL.
- Production is deployed through GitHub Actions -> Harbor -> GitOps -> ArgoCD.
- There is a separate web application deployment and scheduler deployment.
- APScheduler and background jobs are production-critical.
- `render.yaml` and `ProcFile` are legacy and not used for deployment; do not change them.

## Environments

- You are working in a local development environment, not production.
- The app and its PostgreSQL database run in Docker Compose on this machine; the database is a copy of production data.
- In development, the scheduler, outbound email (Brevo) and Web Push notifications must stay disabled. Never enable them.
- The rules below that restrict database commands apply to production. Against the local Docker database you may run migrations, queries and `psql` as needed for the task.

## Safety

- Never access, modify, query, migrate, reset, or delete the production database.
- Never run `create_db.py`.
- Never run `db.drop_all()` or destructive SQL, including against the local database.
- Never run `flask db upgrade` against production.
- Never use `kubectl`, `argocd`, `ssh`, or production credentials unless the user explicitly requests it.
- Never deploy to production automatically.
- Never push directly to `main` without explicit user approval.
- Never modify secrets, credentials, VAPID keys, API keys, or environment variables without explicit approval.
- Never commit secrets or private keys.
- Never send real email or push notifications, and never call external providers from tests.

## Development

- Inspect the existing implementation before modifying code.
- Prefer small, targeted changes over broad refactors.
- Preserve existing behavior unless the requested task requires changing it.
- Consider both the web process and scheduler process when changing scheduled jobs.
- Use SQLAlchemy migrations for schema changes; never recreate the database.
- Do not assume pytest is safe because `test_email.py` may contact an external provider.
- Before running tests or scripts, inspect what they execute.
- Do not make unrelated cleanup changes while working on a task.

## Git

- Commit to the current branch in logical steps with clear messages.
- Show the proposed changes or diff before committing when practical.
- Do not push or merge without explicit user approval.
- Keep bug fixes isolated from unrelated refactoring.

