export interface Toast {
  id: number;
  message: string;
  status: string;
}

export function Notifications({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="toasts">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.status}`}>
          {t.message}
        </div>
      ))}
    </div>
  );
}
