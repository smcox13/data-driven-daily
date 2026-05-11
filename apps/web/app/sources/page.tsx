import { getSources } from "@/lib/api";

export default async function SourcesPage() {
  const sources = await getSources();

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Source Management</p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Manage the discovery surface</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate">
          Editors can add, remove, disable, and annotate RSS or manual sources. Authority scores influence ranking, while
          blocklists remove off-topic domains, authors, or recurring themes from ingestion.
        </p>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        {sources.map((source) => (
          <article key={source.id} className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-2xl font-semibold text-ink">{source.name}</h3>
                <a href={source.url} className="mt-2 block text-sm text-brand underline underline-offset-4">
                  {source.url}
                </a>
              </div>
              <span className={`rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] ${source.enabled ? "bg-brand/10 text-brand" : "bg-slate-200 text-slate"}`}>
                {source.enabled ? "Enabled" : "Paused"}
              </span>
            </div>
            <div className="mt-6 grid gap-4 rounded-2xl bg-mist p-4 text-sm text-slate sm:grid-cols-3">
              <div>
                <div className="text-xs uppercase tracking-[0.16em] text-slate-500">Type</div>
                <div className="mt-1 font-medium text-ink">{source.type}</div>
              </div>
              <div>
                <div className="text-xs uppercase tracking-[0.16em] text-slate-500">Authority</div>
                <div className="mt-1 font-medium text-ink">{source.authority_score.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-xs uppercase tracking-[0.16em] text-slate-500">Notes</div>
                <div className="mt-1 font-medium text-ink">{source.notes ?? "No notes yet"}</div>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

