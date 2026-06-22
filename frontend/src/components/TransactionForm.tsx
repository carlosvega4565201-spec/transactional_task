import { useState, type FormEvent } from "react";
import { createTransaction } from "../api";

const TYPES = ["credit", "debit", "transfer", "payment"];

export function TransactionForm() {
  const [userId, setUserId] = useState("user-1");
  const [amount, setAmount] = useState("100");
  const [type, setType] = useState(TYPES[0]);
  const [async_, setAsync] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await createTransaction(
        {
          user_id: userId,
          amount: Number(amount),
          type,
          // A fresh idempotency key per submission; reusing one is safely a no-op.
          idempotency_key: crypto.randomUUID(),
        },
        async_,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card" onSubmit={submit}>
      <h2>New transaction</h2>
      <div className="row">
        <label>
          User ID
          <input value={userId} onChange={(e) => setUserId(e.target.value)} required />
        </label>
        <label>
          Amount
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
        </label>
        <label>
          Type
          <select value={type} onChange={(e) => setType(e.target.value)}>
            {TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="checkbox">
        <input
          type="checkbox"
          checked={async_}
          onChange={(e) => setAsync(e.target.checked)}
        />
        Process asynchronously (queue + worker)
      </label>
      <button type="submit" disabled={busy}>
        {busy ? "Submitting…" : "Create transaction"}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
