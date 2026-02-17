import asyncio
import logging
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.transaction_service import transaction_service

settings = get_settings()
log = logging.getLogger(__name__)


async def process_with_delay(txn_id: str) -> None:
    await asyncio.sleep(settings.PROCESS_DELAY_SECONDS)
    async with SessionLocal() as db:
        try:
            await transaction_service.process(db, txn_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            try:
                await transaction_service.process(db, txn_id, error=str(e)[:250])
                await db.commit()
            except Exception:
                await db.rollback()
                log.exception("Failed to mark transaction %s", txn_id)


async def recovery_once() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.PROCESS_DELAY_SECONDS)
    async with SessionLocal() as db:
        try:
            due = await transaction_service.due(db, cutoff)
            for tx in due:
                await transaction_service.process(db, tx.transaction_id)
            if due:
                await db.commit()
        except Exception:
            await db.rollback()
            log.exception("Recovery loop failed")


async def recovery_loop() -> None:
    while True:
        await recovery_once()
        await asyncio.sleep(settings.PROCESS_INTERVAL_SECONDS)
