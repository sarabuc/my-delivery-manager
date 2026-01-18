const steps = [
  "Repositories",
  "Content",
  "Submodules",
  "Execution",
  "Submodule Updates",
  "CI",
  "Finalize"
];

export function Stepper({ current }: { current: number }) {
  return (
    <ol className="flex flex-wrap gap-4 text-sm">
      {steps.map((label, index) => {
        const step = index + 1;
        const active = step === current;
        const completed = step < current;
        return (
          <li
            key={label}
            className={`flex items-center gap-2 rounded-full border px-3 py-1 ${
              active
                ? "border-brand-500 bg-brand-500 text-white"
                : completed
                  ? "border-emerald-500 bg-emerald-50 text-emerald-700"
                  : "border-slate-200 bg-white text-slate-500"
            }`}
          >
            <span className="text-xs font-semibold">{step}</span>
            <span>{label}</span>
          </li>
        );
      })}
    </ol>
  );
}
