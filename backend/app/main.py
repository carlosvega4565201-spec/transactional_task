import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import assistant, transactions
from .websocket import manager, redis_subscriber


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    subscriber = asyncio.create_task(redis_subscriber())
    try:
        yield
    finally:
        subscriber.cancel()


app = FastAPI(title="Transactional API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(assistant.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


@app.websocket("/transactions/stream")
async def transactions_stream(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
