import { NewsletterEditor } from "@/components/newsletter-editor";
import { getDraft } from "@/lib/api";
import { notFound } from "next/navigation";

export default async function DraftEditorPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const draft = await getDraft(id);
  if (!draft) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Draft Editor</p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Structured issue editing with a clean escape hatch to raw HTML</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate">
          The editor keeps the featured insight, quick hits, TL;DR, and Data Corner in a fixed structure for speed. If an editor
          needs full markup control, the HTML override becomes the active body version for that issue.
        </p>
      </section>

      <NewsletterEditor draft={draft} />
    </div>
  );
}
