import type { ReactNode } from "react";

export function StepCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-base font-semibold text-slate-900">{title}</h2>
      <div className="mt-4 space-y-4 text-sm text-slate-600">{children}</div>
    </section>
  );
}
