import uuid

async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_create_transaction(client):
    res = await client.post(
        "/transactions/create",
        json={"user_id": "u1", "amount": 10.0, "type": "credit"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == "u1"
    assert body["status"] == "processed"
    assert body["id"] > 0


async def test_create_is_idempotent(client):
    key = str(uuid.uuid4())
    payload = {
        "user_id": "u2",
        "amount": 25.0,
        "type": "debit",
        "idempotency_key": key,
    }

    first = await client.post("/transactions/create", json=payload)
    second = await client.post("/transactions/create", json=payload)

    assert first.status_code == 200 and second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


async def test_idempotency_via_header(client):
    key = str(uuid.uuid4())
    body = {"user_id": "u3", "amount": 5.0, "type": "payment"}
    headers = {"Idempotency-Key": key}

    first = await client.post("/transactions/create", json=body, headers=headers)
    second = await client.post("/transactions/create", json=body, headers=headers)
    assert first.json()["id"] == second.json()["id"]


async def test_async_process_starts_pending(client):
    res = await client.post(
        "/transactions/async-process",
        json={"user_id": "u4", "amount": 99.0, "type": "transfer"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "pending"


async def test_summarize_logs_request(client):
    res = await client.post(
        "/assistant/summarize",
        json={"text": "FastAPI makes building APIs fast. It uses Python type hints."},
    )
    assert res.status_code == 200
    body = res.json()
    assert "summary" in body
    assert body["log_id"] > 0


async def test_invalid_amount_rejected(client):
    res = await client.post(
        "/transactions/create",
        json={"user_id": "u5", "amount": -1, "type": "credit"},
    )
    assert res.status_code == 422
