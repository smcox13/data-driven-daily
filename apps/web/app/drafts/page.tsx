import Link from "next/link";

import { DraftGeneratorPanel } from "@/components/draft-generator-panel";
import { getDrafts } from "@/lib/api";

export default async function DraftsPage() {
  const drafts = await getDrafts();

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Draft Pipeline</p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Generate, revisit, and export issues from one place</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate">
          This view is the operating center for issue creation. Generate a new draft from the ranked article pool, then open any
          existing issue for structured editing, HTML override, and export.
        </p>
      </section>

      <DraftGeneratorPanel />

      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Existing Drafts</p>
            <h3 className="mt-2 text-2xl font-semibold text-ink">Open an issue and keep editing</h3>
          </div>
          <div className="rounded-full bg-mist px-4 py-2 text-sm text-slate">{drafts.length} drafts</div>
        </div>

        <div className="mt-6 space-y-4">
          {drafts.map((draft) => (
            <div key={draft.id} className="rounded-2xl border border-slate-200 p-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-ink">{draft.title}</h4>
                  <p className="mt-1 text-sm text-slate">Selected subject: {draft.selected_subject_line ?? "Not chosen yet"}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="rounded-full bg-mist px-4 py-2 text-sm text-slate">{draft.status}</div>
                  <Link href={`/drafts/${draft.id}`} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
                    Open editor
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

