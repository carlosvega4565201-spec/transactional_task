import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    QUEUE_NAME: str = os.getenv("QUEUE_NAME", "transactions:queue")
    EVENTS_CHANNEL: str = os.getenv("EVENTS_CHANNEL", "transactions:events")

    WORKER_SLEEP_SECONDS: float = float(os.getenv("WORKER_SLEEP_SECONDS", "3"))
    FAILURE_RATE: float = float(os.getenv("FAILURE_RATE", "0.15"))


settings = Settings()
