# Webhook Processor (FastAPI)

## Overview
Receives transaction webhooks, responds fast with `202`, processes transactions in the background with a 30s delay, and stores results. Idempotency is enforced via a unique `transaction_id`.

## Live Deployment
Cloud Run URL: `https://webhook-processor-820256992821.us-central1.run.app`

## Tech Choices
- FastAPI + async SQLAlchemy
- Alembic migrations
- SQLite local, Cloud SQL Postgres in production
- In-process background task + recovery loop

## One-Command Start (Docker Compose)
```bash
docker compose up --build
```
This starts Postgres, runs migrations, and launches the API on `http://localhost:8000`.

## Local Setup (Optional)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Quick API Tests
```bash
bash api_tests.sh
```

### Install package (for pytest/alembic imports)
```bash
pip install -e .
```

## API
- `POST /v1/webhooks/transactions`
- `GET /v1/transactions/{transaction_id}`
- `GET /`

## Notes
- Duplicate webhooks do not trigger duplicate processing.
- A recovery loop ensures pending transactions are processed after restarts.
