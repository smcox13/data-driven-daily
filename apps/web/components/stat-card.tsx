type StatCardProps = {
  label: string;
  value: string;
  helper: string;
};

export function StatCard({ label, value, helper }: StatCardProps) {
  return (
    <div className="rounded-[28px] border border-white/70 bg-white/90 p-6 shadow-panel">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">{label}</p>
      <p className="mt-4 text-4xl font-semibold text-ink">{value}</p>
      <p className="mt-3 text-sm leading-6 text-slate">{helper}</p>
    </div>
  );
}

