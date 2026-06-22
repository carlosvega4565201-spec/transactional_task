import type { Transaction } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const WS_URL =
  import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/transactions/stream";

export interface NewTransaction {
  user_id: string;
  amount: number;
  type: string;
  idempotency_key?: string;
}

export async function listTransactions(): Promise<Transaction[]> {
  const res = await fetch(`${API_URL}/transactions`);
  if (!res.ok) throw new Error(`List failed: ${res.status}`);
  return res.json();
}

export async function createTransaction(
  body: NewTransaction,
  async_: boolean,
): Promise<Transaction> {
  const path = async_ ? "/transactions/async-process" : "/transactions/create";
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Create failed: ${res.status}`);
  return res.json();
}
