import asyncio
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.transaction import Ack, TransactionIn, TransactionOut
from app.services.transaction_service import transaction_service
from app.tasks.processor import process_with_delay

router = APIRouter()


@router.post("/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED, response_model=Ack)
async def webhook(tx: TransactionIn, db: AsyncSession = Depends(get_db)):
    _, created = await transaction_service.create(db, tx)
    if created:
        asyncio.create_task(process_with_delay(tx.transaction_id))
    return Ack()


@router.get("/transactions/{transaction_id}", response_model=list[TransactionOut])
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    tx = await transaction_service.get(db, transaction_id)
    return [tx] if tx else []
