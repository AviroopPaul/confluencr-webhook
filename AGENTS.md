# Confluencr Webhook Processor - Agent Notes

**Context**
- FastAPI service that receives transaction webhooks, responds with 202, and processes transactions asynchronously with a delay.
- Default DB is SQLite via async SQLAlchemy (`sqlite+aiosqlite:///./app.db`).
- Background processing uses `asyncio.create_task` and a recovery loop to handle restarts.

**Key Endpoints**
- `POST /v1/webhooks/transactions` accepts the transaction payload and returns `202`.
- `GET /v1/transactions/{transaction_id}` returns a list with transaction status.
- `GET /` returns health status with UTC time.

**Important Files**
- `app/main.py` app and health check.
- `app/api/v1/endpoints/transactions.py` webhook + status endpoints.
- `app/tasks/processor.py` async processing + recovery loop.
- `app/models/transaction.py` model + status enum.
- `tests/test_webhook.py` core functional tests.

**Local Setup**
- Create venv: `python3 -m venv .venv`
- Install deps: `. .venv/bin/activate && pip install -r requirements.txt`
- Run server: `. .venv/bin/activate && uvicorn app.main:app --reload`

**Tests**
- Run: `. .venv/bin/activate && pytest -q`
- Current test suite is in-process (ASGITransport), so latency checks are application-level only, not real network latency.

**Requirements Coverage Notes**
- Idempotency enforced by unique `transaction_id`.
- Processing delay configurable via `PROCESS_DELAY_SECONDS` in `app/core/config.py`.
- Recovery loop processes due transactions after restarts.

**Environment**
- Optional `DATABASE_URL` override for Postgres or other async DBs.
- Alembic migrations are provided in `alembic/`.
