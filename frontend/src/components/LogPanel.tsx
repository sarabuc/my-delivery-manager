export function LogPanel({ logs }: { logs: string[] }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-900 p-4 text-xs text-slate-100">
      <p className="mb-2 text-[10px] uppercase text-slate-400">Execution Logs</p>
      <div className="space-y-1 max-h-56 overflow-y-auto">
        {logs.length === 0 ? (
          <p className="text-slate-400">No logs yet.</p>
        ) : (
          logs.map((line, index) => (
            <p key={`${line}-${index}`} className="font-mono">
              {line}
            </p>
          ))
        )}
      </div>
    </div>
  );
}
