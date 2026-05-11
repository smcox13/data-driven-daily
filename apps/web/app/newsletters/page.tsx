import { getNewsletters } from "@/lib/api";

export default async function NewslettersPage() {
  const newsletters = await getNewsletters();

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Archive</p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Immutable snapshots for every exported issue</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate">
          Once a newsletter is exported, it becomes a searchable historical record. Archived issues should be discoverable by date,
          keyword, subject line, and category, but never silently editable.
        </p>
      </section>

      <div className="space-y-4">
        {newsletters.map((newsletter) => (
          <article key={newsletter.id} className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand">{newsletter.issue_date}</p>
                <h3 className="mt-2 text-2xl font-semibold text-ink">{newsletter.subject_line}</h3>
                <p className="mt-2 text-sm text-slate">Export format: {String(newsletter.export_metadata.format ?? "html")}</p>
              </div>
              <a
                href={`data:text/html;charset=utf-8,${encodeURIComponent(newsletter.html)}`}
                download={`newsletter-${newsletter.issue_date}.html`}
                className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white"
              >
                Download HTML
              </a>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

