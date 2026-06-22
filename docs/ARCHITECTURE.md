# Architecture & Technical Decisions

## System diagram

```
                     ┌─────────────────────────┐
                     │   React + Vite frontend  │
                     │  (form · list · toasts)  │
                     └────────┬───────────▲─────┘
                  HTTP (REST) │           │ WebSocket
                              ▼           │ (live updates)
                     ┌────────────────────┴─────┐
                     │      FastAPI (API)        │
                     │  /transactions/* ·        │
                     │  /assistant/summarize     │
                     │  /transactions/stream(WS) │
                     └───┬───────────┬───────────┘
            SQL (async)  │           │  Redis
                         ▼           ▼
                 ┌──────────────┐  ┌──────────────────────────┐
                 │   SQLite     │  │          Redis           │
                 │ transactions │  │  list  -> job queue      │
                 │ assistant_   │  │  pub/sub -> event bus    │
                 │   logs       │  └───────▲──────────┬───────┘
                 └──────▲───────┘    publish│     pop  │
                        │ SQL              │          ▼
                        │            ┌─────┴──────────────────┐
                        └────────────┤        Worker          │
                                     │ sleep -> update status │
                                     │ -> publish event       │
                                     └────────────────────────┘
```

## Request flows

**Synchronous create — `POST /transactions/create`**
1. Look up the idempotency key (body field or `Idempotency-Key` header). If a row
   already exists, return it unchanged.
2. Otherwise insert a row with status `processed` and commit.
3. Publish a `created` event to Redis pub/sub → relayed to all websocket clients.

**Async processing — `POST /transactions/async-process`**
1. Same idempotency check.
2. Insert a `pending` row, publish `created`, and `LPUSH` a job onto the Redis list.
3. The worker `BRPOP`s the job, sleeps (simulated work), randomly marks it
   `processed`/`failed`, commits, and publishes an `updated` event.
4. The API relays the event; the browser updates the row and shows a toast.

**Real-time stream — `WS /transactions/stream`**
- The worker lives in a separate process and cannot touch the API's in-memory
  socket set. So every component publishes to a Redis pub/sub channel, and the
  API runs one background subscriber that fans messages out to all sockets.
  This is the key design choice that makes updates work across processes.

## Technical decisions & trade-offs

| Decision | Why | Trade-off |
|---|---|---|
| **FastAPI** | Async-native, automatic OpenAPI docs at `/docs`, first-class WebSocket support. | — |
| **Idempotency via unique key** | A DB unique constraint is the simplest correct guarantee — even a race between two identical requests collapses to one row (caught via `IntegrityError`). | Requires the client to send a key (we auto-generate a UUID per submit in the UI). |
| **Redis list as the queue** | `LPUSH`/`BRPOP` is a reliable, minimal queue — no extra broker to model. | No automatic retries/dead-letter; a full broker (RabbitMQ/Celery) would add those. |
| **Redis pub/sub for websockets** | Decouples the API and worker processes; scales to multiple API replicas. | Pub/sub is fire-and-forget — a client offline at publish time misses the event (it still gets current state on reload via `GET /transactions`). |
| **SQLite (async, WAL)** | Zero-config, fits a take-home; WAL + busy-timeout lets the API and worker share one file. | Not for high write concurrency; swapping `DATABASE_URL` to Postgres needs no code change. |
| **Simulated summarizer** | Runs fully offline, deterministic for the demo and RPA flow. | Not a real LLM; swapping in OpenAI means editing only `summarizer.py`. |
| **Playwright (RPA)** | Modern, reliable auto-waiting; drives the real Wikipedia search box. | Needs a browser download (`playwright install chromium`). |

## Where to extend

- **Real OpenAI**: replace `summarize_text` in `backend/app/summarizer.py` with a
  `client.chat.completions.create(...)` call gated on `OPENAI_API_KEY`.
- **Durable queue**: swap the Redis list for RabbitMQ + a Celery worker; the
  `enqueue_job` / worker boundary is already isolated.
- **Postgres**: change `DATABASE_URL` (e.g. `postgresql+asyncpg://...`) — models
  and queries are backend-agnostic.
