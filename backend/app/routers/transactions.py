from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..events import enqueue_job, publish_event
from ..models import Transaction
from ..schemas import TransactionCreate, TransactionOut, serialize_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


async def _find_by_key(session: AsyncSession, key: str | None) -> Transaction | None:
    if not key:
        return None
    result = await session.execute(
        select(Transaction).where(Transaction.idempotency_key == key)
    )
    return result.scalar_one_or_none()


@router.get("", response_model=list[TransactionOut])
async def list_transactions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Transaction).order_by(Transaction.id.desc())
    )
    return result.scalars().all()


@router.post("/create", response_model=TransactionOut)
async def create_transaction(
    payload: TransactionCreate,
    session: AsyncSession = Depends(get_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    """Create a transaction synchronously. Idempotent via a unique key supplied
    either in the body (`idempotency_key`) or the `Idempotency-Key` header.
    """
    key = payload.idempotency_key or idempotency_key

    existing = await _find_by_key(session, key)
    if existing:
        return existing

    tx = Transaction(
        user_id=payload.user_id,
        amount=payload.amount,
        type=payload.type,
        status="processed",
        idempotency_key=key,
    )
    session.add(tx)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return await _find_by_key(session, key)

    await session.refresh(tx)
    await publish_event({"event": "created", "transaction": serialize_transaction(tx)})
    return tx


@router.post("/async-process", response_model=TransactionOut)
async def async_process(
    payload: TransactionCreate,
    session: AsyncSession = Depends(get_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    key = payload.idempotency_key or idempotency_key

    existing = await _find_by_key(session, key)
    if existing:
        return existing

    tx = Transaction(
        user_id=payload.user_id,
        amount=payload.amount,
        type=payload.type,
        status="pending",
        idempotency_key=key,
    )
    session.add(tx)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return await _find_by_key(session, key)

    await session.refresh(tx)
    await publish_event({"event": "created", "transaction": serialize_transaction(tx)})
    await enqueue_job({"transaction_id": tx.id})
    return tx
