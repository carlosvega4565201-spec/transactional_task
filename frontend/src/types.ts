export interface Transaction {
  id: number;
  user_id: string;
  amount: number;
  type: string;
  status: "pending" | "processed" | "failed" | string;
  idempotency_key: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionEvent {
  event: "created" | "updated";
  transaction: Transaction;
}
