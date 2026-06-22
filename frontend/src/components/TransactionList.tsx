import type { Transaction } from "../types";

const STATUS_COLORS: Record<string, string> = {
  pending: "#b58900",
  processed: "#2aa198",
  failed: "#dc322f",
};

export function TransactionList({ items }: { items: Transaction[] }) {
  return (
    <div className="card">
      <h2>Transactions ({items.length})</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Amount</th>
            <th>Type</th>
            <th>Status</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 && (
            <tr>
              <td colSpan={6} className="empty">
                No transactions yet.
              </td>
            </tr>
          )}
          {items.map((t) => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>{t.user_id}</td>
              <td>{t.amount.toFixed(2)}</td>
              <td>{t.type}</td>
              <td>
                <span
                  className="badge"
                  style={{ background: STATUS_COLORS[t.status] ?? "#657b83" }}
                >
                  {t.status}
                </span>
              </td>
              <td>{new Date(t.updated_at).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
