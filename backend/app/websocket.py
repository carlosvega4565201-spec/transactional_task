import asyncio

from fastapi import WebSocket

from .config import settings
from .events import get_redis


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self.active.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self.active.discard(ws)

    async def broadcast(self, message: str) -> None:
        async with self._lock:
            targets = list(self.active)
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                await self.disconnect(ws)


manager = ConnectionManager()


async def redis_subscriber() -> None:
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(settings.EVENTS_CHANNEL)
    async for message in pubsub.listen():
        if message.get("type") == "message":
            await manager.broadcast(message["data"])
