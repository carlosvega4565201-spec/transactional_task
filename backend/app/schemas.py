from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Transaction

VALID_TYPES = {"credit", "debit", "transfer", "payment"}


class TransactionCreate(BaseModel):
    user_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    type: str = Field(min_length=1)
    idempotency_key: str | None = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    amount: float
    type: str
    status: str
    idempotency_key: str | None
    created_at: datetime
    updated_at: datetime


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)


class SummarizeResponse(BaseModel):
    summary: str
    log_id: int


def serialize_transaction(tx: Transaction) -> dict:
    return TransactionOut.model_validate(tx).model_dump(mode="json")
