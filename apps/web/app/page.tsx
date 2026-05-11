import Link from "next/link";

import { DraftGeneratorPanel } from "@/components/draft-generator-panel";
import { StatCard } from "@/components/stat-card";
import { getArticles, getDrafts, getNewsletters, getSources } from "@/lib/api";

export default async function DashboardPage() {
  const [sources, articles, drafts, newsletters] = await Promise.all([
    getSources(),
    getArticles(),
    getDrafts(),
    getNewsletters()
  ]);

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-ink px-8 py-10 text-white shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-200">Executive Workflow</p>
        <h2 className="mt-3 max-w-4xl font-serif text-4xl leading-tight">
          Move from ranked industry stories to a human-approved, Mailchimp-ready newsletter in one editor session.
        </h2>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">
          This workspace is structured around one organization, one editorial team, and a fast review loop: discover, rank,
          summarize, curate, preview, export, archive.
        </p>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Active Sources" value={String(sources.length)} helper="RSS and manual sources feed the discovery queue." />
        <StatCard label="Ranked Articles" value={String(articles.length)} helper="Duplicates are suppressed while replacements stay searchable." />
        <StatCard label="Open Drafts" value={String(drafts.length)} helper="Structured issues stay editable until HTML override or export." />
        <StatCard label="Archive Issues" value={String(newsletters.length)} helper="Exports become immutable newsletter snapshots." />
      </section>

      <DraftGeneratorPanel />

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Draft Pipeline</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Current editorial momentum</h3>
            </div>
            <Link
              href={drafts[0] ? `/drafts/${drafts[0].id}` : "/drafts"}
              className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white"
            >
              {drafts[0] ? "Open latest draft" : "Open drafts"}
            </Link>
          </div>
          <div className="mt-6 space-y-4">
            {drafts.map((draft) => (
              <div key={draft.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <h4 className="text-lg font-semibold text-ink">{draft.title}</h4>
                    <p className="mt-1 text-sm text-slate">Selected subject: {draft.selected_subject_line}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-mist px-4 py-2 text-sm text-slate">{draft.status}</div>
                    <Link href={`/drafts/${draft.id}`} className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-ink">
                      Open
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Top Ranked Articles</p>
          <div className="mt-5 space-y-4">
            {articles.slice(0, 3).map((article) => (
              <div key={article.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="text-sm font-semibold text-brand">Rank {article.ranking_score.toFixed(2)}</div>
                <a href={article.url} className="mt-2 block text-lg font-semibold text-ink underline decoration-brand/30 underline-offset-4">
                  {article.title}
                </a>
                <p className="mt-2 text-sm leading-6 text-slate">{article.excerpt}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
