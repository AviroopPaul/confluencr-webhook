from datetime import datetime, timedelta, timezone
import time
import asyncio
import pytest
from sqlalchemy import select
from app.models.transaction import Transaction, TxStatus
from app.tasks import processor
from app.services.transaction_service import transaction_service
from conftest import TestSessionLocal


BASE = {
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR",
}


@pytest.mark.asyncio
async def test_webhook_and_status(client, db_session):
    payload = {"transaction_id": "txn_status_001", **BASE}
    r = await client.post("/v1/webhooks/transactions", json=payload)
    assert r.status_code == 202

    r = await client.get(f"/v1/transactions/{payload['transaction_id']}")
    body = r.json()
    assert body and body[0]["status"] == "PROCESSING"


@pytest.mark.asyncio
async def test_duplicate_webhook_no_dup_rows(client, db_session):
    payload = {"transaction_id": "txn_dup_001", **BASE}
    await client.post("/v1/webhooks/transactions", json=payload)
    await client.post("/v1/webhooks/transactions", json=payload)
    res = await db_session.execute(
        select(Transaction).where(Transaction.transaction_id == payload["transaction_id"])
    )
    assert len(res.scalars().all()) == 1


@pytest.mark.asyncio
async def test_processing_delay_and_completion(client, db_session, monkeypatch):
    monkeypatch.setattr(processor.settings, "PROCESS_DELAY_SECONDS", 0.2, raising=False)
    payload = {"transaction_id": "txn_delay_001", **BASE}
    await client.post("/v1/webhooks/transactions", json=payload)

    r = await client.get(f"/v1/transactions/{payload['transaction_id']}")
    assert r.json()[0]["status"] == "PROCESSING"

    await asyncio.sleep(0.25)
    r = await client.get(f"/v1/transactions/{payload['transaction_id']}")
    assert r.json()[0]["status"] == "PROCESSED"


@pytest.mark.asyncio
async def test_webhook_fast_response(client, monkeypatch):
    monkeypatch.setattr(processor.settings, "PROCESS_DELAY_SECONDS", 0.2, raising=False)
    payload = {"transaction_id": "txn_fast_001", **BASE}
    start = time.perf_counter()
    r = await client.post("/v1/webhooks/transactions", json=payload)
    elapsed = time.perf_counter() - start
    assert r.status_code == 202
    assert elapsed < 0.5


@pytest.mark.asyncio
async def test_processing_failure_marks_failed(client, db_session, monkeypatch):
    monkeypatch.setattr(processor.settings, "PROCESS_DELAY_SECONDS", 0.01, raising=False)
    orig = transaction_service.process
    state = {"raised": False}

    async def fail_once(db, txn_id: str, error: str | None = None):
        if error is None and not state["raised"]:
            state["raised"] = True
            raise RuntimeError("boom")
        return await orig(db, txn_id, error)

    monkeypatch.setattr(transaction_service, "process", fail_once)

    payload = {"transaction_id": "txn_fail_001", **BASE}
    await client.post("/v1/webhooks/transactions", json=payload)
    await asyncio.sleep(0.05)

    r = await client.get(f"/v1/transactions/{payload['transaction_id']}")
    body = r.json()[0]
    assert body["status"] == "FAILED"
    assert body["error"]


@pytest.mark.asyncio
async def test_recovery_processes_due(db_session, monkeypatch):
    monkeypatch.setattr(processor, "SessionLocal", TestSessionLocal)
    old = datetime.now(timezone.utc) - timedelta(seconds=60)
    payload = {"transaction_id": "txn_recovery_001", **BASE}
    tx = Transaction(**payload, status=TxStatus.PROCESSING, created_at=old)
    db_session.add(tx)
    await db_session.commit()

    await processor.recovery_once()
    await db_session.refresh(tx)
    assert tx.status == TxStatus.PROCESSED
