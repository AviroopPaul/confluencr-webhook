from datetime import datetime, timezone
from app.models.transaction import TxStatus
from app.repositories.transaction_repository import transaction_repo
from app.schemas.transaction import TransactionIn


class TransactionService:
    async def create(self, db, tx_in: TransactionIn):
        return await transaction_repo.create_if_not_exists(db, tx_in.model_dump())

    async def get(self, db, txn_id: str):
        return await transaction_repo.get_by_txn_id(db, txn_id)

    async def process(self, db, txn_id: str, error: str | None = None):
        status = TxStatus.FAILED if error else TxStatus.PROCESSED
        return await transaction_repo.mark_processed(db, txn_id, status=status, error=error, processed_at=datetime.now(timezone.utc))

    async def due(self, db, cutoff: datetime):
        return await transaction_repo.get_due(db, cutoff)


transaction_service = TransactionService()
