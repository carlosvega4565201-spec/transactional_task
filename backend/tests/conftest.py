import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

for _f in ("test.db", "test.db-wal", "test.db-shm"):
    if os.path.exists(_f):
        os.remove(_f)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import database
from app.main import app
from app.routers import transactions as tx_router


@pytest_asyncio.fixture
async def client(monkeypatch):
    await database.init_db()

    async def _noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(tx_router, "publish_event", _noop)
    monkeypatch.setattr(tx_router, "enqueue_job", _noop)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
