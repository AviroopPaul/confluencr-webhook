from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.transaction import TxStatus


class TransactionIn(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str


class TransactionOut(TransactionIn):
    status: TxStatus
    created_at: datetime
    processed_at: datetime | None = None
    error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Ack(BaseModel):
    status: str = "ACCEPTED"
