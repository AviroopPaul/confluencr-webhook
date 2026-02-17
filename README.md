# Webhook Processor (FastAPI)

## Overview
Receives transaction webhooks, responds fast with `202`, processes transactions in the background with a 30s delay, and stores results. Idempotency is enforced via a unique `transaction_id`.

## Tech Choices
- FastAPI + async SQLAlchemy
- Alembic migrations
- SQLite local, Cloud SQL Postgres in production
- In-process background task + recovery loop

## Local Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure DB (optional)
Default is SQLite: `sqlite+aiosqlite:///./app.db`.
To override:
```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname"
```

### Migrations
```bash
alembic upgrade head
```

### Run
```bash
uvicorn app.main:app --reload
```

### Quick API Tests
```bash
bash api_tests.sh
```

### Install package (for pytest/alembic imports)
```bash
pip install -e .
```

## Cloud Run (Cloud SQL Postgres)
1. Build and push image.
2. Deploy:
```bash
gcloud run deploy webhook-processor \
  --image gcr.io/PROJECT_ID/IMAGE:TAG \
  --region REGION \
  --add-cloudsql-instances INSTANCE_CONNECTION_NAME \
  --set-env-vars DATABASE_URL="postgresql+asyncpg://USER:PASSWORD@/DB?host=/cloudsql/INSTANCE_CONNECTION_NAME"
```

## API
- `POST /v1/webhooks/transactions`
- `GET /v1/transactions/{transaction_id}`
- `GET /`

## Notes
- Duplicate webhooks do not trigger duplicate processing.
- A recovery loop ensures pending transactions are processed after restarts.
