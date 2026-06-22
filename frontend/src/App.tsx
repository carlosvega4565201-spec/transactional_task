import { useCallback, useEffect, useRef, useState } from "react";
import { WS_URL, listTransactions } from "./api";
import { useWebSocket } from "./hooks/useWebSocket";
import { TransactionForm } from "./components/TransactionForm";
import { TransactionList } from "./components/TransactionList";
import { Notifications, type Toast } from "./components/Notifications";
import type { Transaction, TransactionEvent } from "./types";

export default function App() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const toastId = useRef(0);

  const pushToast = useCallback((message: string, status: string) => {
    const id = ++toastId.current;
    setToasts((prev) => [...prev, { id, message, status }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  // Initial load.
  useEffect(() => {
    listTransactions().then(setTransactions).catch(console.error);
  }, []);

  // Merge a transaction from a websocket event into local state.
  const onMessage = useCallback(
    (data: unknown) => {
      const msg = data as TransactionEvent;
      if (!msg?.transaction) return;
      const tx = msg.transaction;

      setTransactions((prev) => {
        const idx = prev.findIndex((t) => t.id === tx.id);
        if (idx === -1) return [tx, ...prev];
        const next = [...prev];
        next[idx] = tx;
        return next;
      });

      if (msg.event === "created") {
        pushToast(`Transaction #${tx.id} created (${tx.status})`, tx.status);
      } else if (msg.event === "updated") {
        pushToast(`Transaction #${tx.id} → ${tx.status}`, tx.status);
      }
    },
    [pushToast],
  );

  const { connected } = useWebSocket(WS_URL, onMessage);

  return (
    <div className="app">
      <header>
        <h1>Transactions Dashboard</h1>
        <span className={`status-dot ${connected ? "on" : "off"}`}>
          {connected ? "live" : "disconnected"}
        </span>
      </header>

      <main>
        <TransactionForm />
        <TransactionList items={transactions} />
      </main>

      <Notifications toasts={toasts} />
    </div>
  );
}
