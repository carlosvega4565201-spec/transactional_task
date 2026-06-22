import asyncio
import json
import random

from app.config import settings
from app.database import AsyncSessionLocal, init_db
from app.events import get_redis, publish_event
from app.models import Transaction
from app.schemas import serialize_transaction


async def process_job(job: dict) -> None:
    tx_id = job.get("transaction_id")
    if tx_id is None:
        return

    # Simulate real work.
    await asyncio.sleep(settings.WORKER_SLEEP_SECONDS)

    new_status = "failed" if random.random() < settings.FAILURE_RATE else "processed"

    async with AsyncSessionLocal() as session:
        tx = await session.get(Transaction, tx_id)
        if tx is None:
            return
        tx.status = new_status
        await session.commit()
        await session.refresh(tx)
        payload = serialize_transaction(tx)

    await publish_event({"event": "updated", "transaction": payload})
    print(f"[worker] transaction {tx_id} -> {new_status}", flush=True)


async def main() -> None:
    await init_db()
    r = await get_redis()
    print("[worker] started; waiting for jobs...", flush=True)

    while True:
        item = await r.brpop(settings.QUEUE_NAME, timeout=5)
        if item is None:
            continue
        _, raw = item
        try:
            await process_job(json.loads(raw))
        except Exception as exc:
            print(f"[worker] error processing job: {exc}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
