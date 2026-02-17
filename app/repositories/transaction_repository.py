from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction, TxStatus


class TransactionRepository:
    async def get_by_txn_id(self, db: AsyncSession, txn_id: str) -> Transaction | None:
        res = await db.execute(select(Transaction).where(Transaction.transaction_id == txn_id))
        return res.scalars().first()

    async def create_if_not_exists(self, db: AsyncSession, data: dict) -> tuple[Transaction, bool]:
        obj = Transaction(**data)
        db.add(obj)
        try:
            await db.flush()
            return obj, True
        except IntegrityError:
            await db.rollback()
            existing = await self.get_by_txn_id(db, data["transaction_id"])
            return existing, False

    async def mark_processed(
        self,
        db: AsyncSession,
        txn_id: str,
        status: TxStatus = TxStatus.PROCESSED,
        error: str | None = None,
        processed_at: datetime | None = None,
    ) -> int:
        stmt = (
            update(Transaction)
            .where(Transaction.transaction_id == txn_id, Transaction.status == TxStatus.PROCESSING)
            .values(
                status=status,
                processed_at=processed_at or datetime.now(timezone.utc),
                error=error,
            )
        )
        res = await db.execute(stmt)
        return res.rowcount or 0

    async def get_due(self, db: AsyncSession, cutoff: datetime) -> list[Transaction]:
        res = await db.execute(
            select(Transaction).where(
                Transaction.status == TxStatus.PROCESSING,
                Transaction.processed_at.is_(None),
                Transaction.created_at <= cutoff,
            )
        )
        return list(res.scalars().all())


transaction_repo = TransactionRepository()
