# Fullstack Technical Test — Transactional API + React + Integrations + RPA

A complete solution covering all four parts of the brief:

| Part | What | Where |
|---|---|---|
| 1 | Python transactional API: idempotent create, async queue + worker, WebSocket stream | `backend/` |
| 2 | React UI: list, create form, live WebSocket updates, toast notifications | `frontend/` |
| 3 | `/assistant/summarize` (simulated OpenAI) with DB request/response logging | `backend/app/routers/assistant.py` |
| 4 | RPA bot: Playwright → Wikipedia → extract paragraph → call the summarize API | `rpa/` |

**Stack:** FastAPI · SQLAlchemy (async) · SQLite · Redis (queue + pub/sub) ·
React + Vite + TypeScript · Playwright.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the diagram and design
decisions, and [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md) for the demo script.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/transactions/create` | Create a transaction. **Idempotent** via `Idempotency-Key` header or `idempotency_key` body field. |
| `POST` | `/transactions/async-process` | Record as `pending`, enqueue to Redis; the worker processes it. |
| `GET` | `/transactions` | List all transactions (used by the UI). |
| `WS` | `/transactions/stream` | WebSocket stream of `created` / `updated` events. |
| `POST` | `/assistant/summarize` | Summarize text (simulated); logs request + response. |
| `GET` | `/health` | Health check. |

Interactive docs (Swagger UI) are auto-generated at **http://localhost:8000/docs**.

---

## Quick start — Docker Compose (recommended)

Prerequisite: **Docker Desktop**.

```bash
docker compose up --build
```

This starts four services: `redis`, `backend` (API on **:8000**), `worker`, and
`frontend` (**:5173**).

- UI:        http://localhost:5173
- API docs:  http://localhost:8000/docs

Stop with `Ctrl+C`; remove volumes with `docker compose down -v`.

Run the RPA bot from the host against the running API:

```bash
cd rpa
pip install -r requirements.txt
playwright install chromium
python rpa_wikipedia.py "Artificial intelligence"
```

---

## Manual run (no Docker)

Prerequisites: **Python 3.11+**, **Node 18+**, and a running **Redis** instance.
On Windows, get Redis via WSL (`sudo apt install redis-server`), Docker
(`docker run -p 6379:6379 redis:7-alpine`), or [Memurai](https://www.memurai.com/).

**1. Backend API**
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Worker** (separate terminal, same venv)
```bash
cd backend
python worker.py
```

**3. Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

**4. RPA** (separate terminal)
```bash
cd rpa
pip install -r requirements.txt
playwright install chromium
python rpa_wikipedia.py "Python (programming language)"
```

> Default connection strings live in `backend/app/config.py` and can be overridden
> via environment variables — see [`.env.example`](.env.example).

---

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest                 # idempotency, async status, summarize, validation
```
The test suite stubs Redis, so **no external services are needed** to run it.

---

## Postman collection

Import [`postman/transactions-api.postman_collection.json`](postman/transactions-api.postman_collection.json).
It includes all HTTP endpoints (with an idempotency demo). The real-time stream is
a WebSocket — test it via Postman's *New → WebSocket Request* at
`ws://localhost:8000/transactions/stream`, or just watch the frontend.

---

## Idempotency — how to verify

POST `/transactions/create` twice with the same key:

```bash
curl -X POST http://localhost:8000/transactions/create \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: demo-1" \
  -d '{"user_id":"user-1","amount":100,"type":"credit"}'
```

Run it again with the same `Idempotency-Key` → you get back the **same `id`**, and
`GET /transactions` shows only one row.

---

## Notes on this environment

The machine this was authored on had only `git` installed (no Python/Node/Docker).
The code is standard and complete; to **run** it, install Docker Desktop (easiest)
or Python + Node + Redis as described above.
