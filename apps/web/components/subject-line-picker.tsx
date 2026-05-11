"use client";

type SubjectLinePickerProps = {
  options: string[];
  selected?: string | null;
  onSelect: (value: string) => void;
};

export function SubjectLinePicker({ options, selected, onSelect }: SubjectLinePickerProps) {
  return (
    <div className="rounded-[24px] border border-slate-200 bg-white p-5">
      <div className="mb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Subject Lines</p>
        <p className="mt-1 text-sm text-slate">Choose the final line, then tune it if needed before export.</p>
      </div>
      <div className="space-y-3">
        {options.map((option) => {
          const isSelected = selected === option;
          return (
            <button
              key={option}
              type="button"
              onClick={() => onSelect(option)}
              className={`w-full rounded-2xl border px-4 py-3 text-left text-sm transition ${
                isSelected
                  ? "border-brand bg-brand/10 text-ink"
                  : "border-slate-200 bg-slate-50 text-slate hover:border-brand/40 hover:bg-brand/5"
              }`}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}

