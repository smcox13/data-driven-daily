"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { PreviewTabs } from "@/components/preview-tabs";
import { SubjectLinePicker } from "@/components/subject-line-picker";
import { TipTapEditor } from "@/components/tiptap-editor";
import type { Draft, ExportResponse } from "@/lib/types";
import { discardHtmlOverride, exportDraft, regenerateDraftContent, saveHtmlOverride, updateDraft } from "@/lib/web-api";

type NewsletterEditorProps = {
  draft: Draft;
};

function buildStructuredPreviewHtml(draft: Draft, structure: Draft["structure_json"], selectedSubjectLine?: string | null) {
  const quickHits = structure.quick_hits
    .map(
      (item) => `
        <div style="padding:0 0 18px;">
          <div style="font-size:18px;font-weight:700;line-height:1.4;margin-bottom:6px;">
            <a href="${item.url}" style="color:#111827;text-decoration:none;">${item.title}</a>
          </div>
          <div style="font-size:15px;line-height:1.7;color:#374151;">${item.summary}</div>
        </div>
      `
    )
    .join("");

  return `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>${selectedSubjectLine ?? draft.title}</title>
      </head>
      <body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f4f6;padding:24px 0;">
          <tr>
            <td align="center">
              <table role="presentation" width="640" cellspacing="0" cellpadding="0" style="width:640px;max-width:640px;background:#ffffff;">
                <tr>
                  <td style="padding:28px;background:#0f172a;color:#ffffff;">
                    <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;color:#cbd5e1;">Data-Driven Daily</div>
                    <h1 style="margin:12px 0 8px;font-size:30px;line-height:1.2;">Executive intelligence for marketing, data, and AI leaders</h1>
                    <div style="color:#cbd5e1;font-size:14px;">Issue date: ${structure.issue_date}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:28px;">
                    <div style="font-size:12px;font-weight:700;text-transform:uppercase;color:#0f766e;margin-bottom:12px;">Featured Insight</div>
                    <h2 style="margin:0 0 12px;font-size:26px;line-height:1.25;">
                      <a href="${structure.featured_insight.url}" style="color:#111827;text-decoration:none;">${structure.featured_insight.title}</a>
                    </h2>
                    <div style="font-size:15px;line-height:1.7;">${structure.featured_insight.summary}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:0 28px 28px;">
                    <div style="font-size:12px;font-weight:700;text-transform:uppercase;color:#0f766e;margin-bottom:12px;">Quick Hits</div>
                    ${quickHits}
                  </td>
                </tr>
                <tr>
                  <td style="padding:24px 28px;background:#fef3c7;">
                    <div style="font-size:12px;font-weight:700;text-transform:uppercase;color:#92400e;margin-bottom:12px;">TL;DR</div>
                    <div style="font-size:15px;line-height:1.7;color:#78350f;">${structure.tldr}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:28px;">
                    <div style="font-size:12px;font-weight:700;text-transform:uppercase;color:#0f766e;margin-bottom:12px;">${structure.cta.headline}</div>
                    <div style="font-size:15px;line-height:1.7;">${structure.cta.body}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
  `;
}

function downloadHtml(html: string, filename: string) {
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function NewsletterEditor({ draft }: NewsletterEditorProps) {
  const router = useRouter();
  const [draftState, setDraftState] = useState(draft);
  const [structure, setStructure] = useState(draft.structure_json);
  const [selectedSubjectLine, setSelectedSubjectLine] = useState(draft.selected_subject_line ?? draft.structure_json.subject_lines[0] ?? "");
  const [htmlOverrideValue, setHtmlOverrideValue] = useState(draft.html_override ?? draft.preview_html ?? "");
  const [htmlMode, setHtmlMode] = useState(Boolean(draft.html_override));
  const [action, setAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [latestExport, setLatestExport] = useState<ExportResponse["snapshot"] | null>(null);

  const structuredEditingLocked = Boolean(draftState.html_override);
  const structuredPreviewHtml = buildStructuredPreviewHtml(draftState, structure, selectedSubjectLine);
  const activePreviewHtml = htmlMode ? htmlOverrideValue : draftState.html_override ?? structuredPreviewHtml;

  function applyDraft(nextDraft: Draft) {
    setDraftState(nextDraft);
    setStructure(nextDraft.structure_json);
    setSelectedSubjectLine(nextDraft.selected_subject_line ?? nextDraft.structure_json.subject_lines[0] ?? "");
    setHtmlOverrideValue(nextDraft.html_override ?? nextDraft.preview_html ?? "");
    setHtmlMode(Boolean(nextDraft.html_override));
  }

  async function runAction<T>(label: string, callback: () => Promise<T>) {
    setAction(label);
    setError(null);
    setNotice(null);
    try {
      return await callback();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong.");
      return null;
    } finally {
      setAction(null);
    }
  }

  function updateQuickHit(index: number, summary: string) {
    setStructure((current) => {
      const next = { ...current, quick_hits: [...current.quick_hits] };
      next.quick_hits[index] = { ...next.quick_hits[index], summary };
      return next;
    });
  }

  function moveQuickHit(index: number, direction: -1 | 1) {
    setStructure((current) => {
      const nextItems = [...current.quick_hits];
      const targetIndex = index + direction;
      if (targetIndex < 0 || targetIndex >= nextItems.length) {
        return current;
      }
      const [item] = nextItems.splice(index, 1);
      nextItems.splice(targetIndex, 0, item);
      return { ...current, quick_hits: nextItems };
    });
  }

  async function handleSaveStructuredDraft() {
    const nextDraft = await runAction("save", () =>
      updateDraft(draftState.id, {
        selected_subject_line: selectedSubjectLine,
        structure_json: structure
      })
    );
    if (nextDraft) {
      applyDraft(nextDraft);
      setNotice("Draft saved.");
      router.refresh();
    }
  }

  async function handleRegenerate(section: "tldr" | "subject_lines", articleId?: string) {
    const nextDraft = await runAction(`regenerate-${section}`, () =>
      regenerateDraftContent(draftState.id, articleId ? { section, article_id: articleId } : { section })
    );
    if (nextDraft) {
      applyDraft(nextDraft);
      setNotice(section === "tldr" ? "TL;DR regenerated." : "Subject lines regenerated.");
      router.refresh();
    }
  }

  async function handleRegenerateSummary(articleId: string) {
    const nextDraft = await runAction("regenerate-summary", () =>
      regenerateDraftContent(draftState.id, { section: "summary", article_id: articleId })
    );
    if (nextDraft) {
      applyDraft(nextDraft);
      setNotice("Summary regenerated.");
      router.refresh();
    }
  }

  async function handleSaveHtmlOverride() {
    if (!htmlOverrideValue.trim()) {
      setError("HTML override cannot be empty.");
      return;
    }
    const nextDraft = await runAction("save-html", () => saveHtmlOverride(draftState.id, htmlOverrideValue));
    if (nextDraft) {
      applyDraft(nextDraft);
      setNotice("HTML override saved. Structured body editing is now locked until you discard it.");
      router.refresh();
    }
  }

  async function handleDiscardHtmlOverride() {
    const nextDraft = await runAction("discard-html", () => discardHtmlOverride(draftState.id));
    if (nextDraft) {
      applyDraft(nextDraft);
      setHtmlMode(false);
      setNotice("HTML override discarded. Structured editing is available again.");
      router.refresh();
    }
  }

  async function handleExport() {
    const savedDraft = await runAction("export", async () => {
      const structuredDraft = await updateDraft(draftState.id, {
        selected_subject_line: selectedSubjectLine,
        structure_json: structure
      });

      let exportTarget = structuredDraft;
      if (htmlMode) {
        exportTarget = await saveHtmlOverride(structuredDraft.id, htmlOverrideValue);
      }

      applyDraft(exportTarget);
      return exportDraft(exportTarget.id);
    });

    if (savedDraft) {
      setLatestExport(savedDraft.snapshot);
      setNotice("Newsletter exported and downloaded as HTML.");
      downloadHtml(savedDraft.mailchimp_html, `data-driven-daily-${savedDraft.snapshot.issue_date}.html`);
      router.refresh();
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_420px]">
      <section className="space-y-6">
        <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
          <div className="flex flex-col gap-4 border-b border-slate-200 pb-5">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Structured Editor</p>
                <h2 className="mt-2 text-2xl font-semibold text-ink">{draftState.title}</h2>
                <p className="mt-2 text-sm text-slate">
                  Save structured changes, regenerate sections, and export HTML without leaving the editor.
                </p>
              </div>
              <div className="rounded-2xl bg-mist px-4 py-3 text-sm text-slate">
                <div>Provider: {draftState.ai_provider}</div>
                <div>Status: {draftState.status}</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleSaveStructuredDraft}
                disabled={action !== null}
                className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                {action === "save" ? "Saving..." : "Save Draft"}
              </button>
              <button
                type="button"
                onClick={() => handleRegenerate("tldr")}
                disabled={action !== null}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-60"
              >
                {action === "regenerate-tldr" ? "Regenerating..." : "Regenerate TL;DR"}
              </button>
              <button
                type="button"
                onClick={() => handleRegenerate("subject_lines")}
                disabled={action !== null}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-60"
              >
                {action === "regenerate-subject_lines" ? "Regenerating..." : "Regenerate Subject Lines"}
              </button>
              <button
                type="button"
                onClick={handleExport}
                disabled={action !== null}
                className="rounded-full bg-brand px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                {action === "export" ? "Exporting..." : "Export HTML"}
              </button>
            </div>

            {structuredEditingLocked ? (
              <div className="rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-900">
                A saved HTML override is active for this draft. Discard it to resume block-level body editing.
              </div>
            ) : null}

            {notice ? <div className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{notice}</div> : null}
            {error ? <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-danger">{error}</div> : null}
            {latestExport ? (
              <div className="rounded-2xl bg-mist px-4 py-3 text-sm text-slate">
                Latest export saved for {latestExport.issue_date}. Check the archive page for the immutable snapshot.
              </div>
            ) : null}
          </div>

          <div className="mt-6 space-y-8">
            <div>
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Featured Insight</p>
                  <h3 className="mt-2 text-2xl font-semibold text-ink">{structure.featured_insight.title}</h3>
                </div>
                <button
                  type="button"
                  onClick={() => handleRegenerateSummary(structure.featured_insight.article_id)}
                  disabled={action !== null || structuredEditingLocked}
                  className="rounded-full border border-slate-300 px-4 py-2 text-xs font-medium text-ink disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {action === "regenerate-summary" ? "Regenerating..." : "Regenerate Summary"}
                </button>
              </div>
              <div className="mt-4">
                {structuredEditingLocked ? (
                  <div
                    className="min-h-[140px] rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-ink"
                    dangerouslySetInnerHTML={{ __html: structure.featured_insight.summary }}
                  />
                ) : (
                  <TipTapEditor
                    value={structure.featured_insight.summary}
                    onChange={(value) =>
                      setStructure((current) => ({
                        ...current,
                        featured_insight: { ...current.featured_insight, summary: value }
                      }))
                    }
                  />
                )}
              </div>
            </div>

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-brand">Quick Hits</p>
              <div className="space-y-5">
                {structure.quick_hits.map((item, index) => (
                  <div key={item.article_id} className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                    <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                      <div>
                        <h4 className="text-lg font-semibold text-ink">{item.title}</h4>
                        <a href={item.url} className="text-sm text-brand underline underline-offset-4">
                          Open source article
                        </a>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => handleRegenerateSummary(item.article_id)}
                          disabled={action !== null || structuredEditingLocked}
                          className="rounded-full border border-slate-300 px-3 py-2 text-xs font-medium text-slate disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Regenerate
                        </button>
                        <button
                          type="button"
                          onClick={() => moveQuickHit(index, -1)}
                          disabled={structuredEditingLocked}
                          className="rounded-full border border-slate-300 px-3 py-2 text-xs font-medium text-slate disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Move up
                        </button>
                        <button
                          type="button"
                          onClick={() => moveQuickHit(index, 1)}
                          disabled={structuredEditingLocked}
                          className="rounded-full border border-slate-300 px-3 py-2 text-xs font-medium text-slate disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Move down
                        </button>
                      </div>
                    </div>
                    <div className="mt-4">
                      {structuredEditingLocked ? (
                        <div
                          className="min-h-[140px] rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-7 text-ink"
                          dangerouslySetInnerHTML={{ __html: item.summary }}
                        />
                      ) : (
                        <TipTapEditor value={item.summary} onChange={(value) => updateQuickHit(index, value)} />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-brand">TL;DR</p>
              <textarea
                value={structure.tldr}
                disabled={structuredEditingLocked}
                onChange={(event) => setStructure((current) => ({ ...current, tldr: event.target.value }))}
                className="min-h-[140px] w-full rounded-[24px] border border-slate-200 bg-white px-4 py-4 text-sm leading-7 text-ink outline-none focus:border-brand disabled:cursor-not-allowed disabled:bg-slate-100"
              />
            </div>

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-brand">Data Corner</p>
              <textarea
                value={structure.cta.body}
                disabled={structuredEditingLocked}
                onChange={(event) =>
                  setStructure((current) => ({
                    ...current,
                    cta: { ...current.cta, body: event.target.value }
                  }))
                }
                className="min-h-[120px] w-full rounded-[24px] border border-slate-200 bg-white px-4 py-4 text-sm leading-7 text-ink outline-none focus:border-brand disabled:cursor-not-allowed disabled:bg-slate-100"
              />
            </div>
          </div>
        </div>

        <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Advanced HTML Mode</p>
              <p className="mt-2 text-sm text-slate">
                Save a manual HTML body when you need email-specific markup control. Once saved, it becomes the active export body until discarded.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setHtmlMode((current) => !current)}
              className={`rounded-full px-4 py-2 text-sm font-medium ${htmlMode ? "bg-ink text-white" : "bg-mist text-slate"}`}
            >
              {htmlMode ? "HTML override on" : "Enable HTML override"}
            </button>
          </div>

          {htmlMode ? (
            <>
              <textarea
                value={htmlOverrideValue}
                onChange={(event) => setHtmlOverrideValue(event.target.value)}
                className="mt-5 min-h-[260px] w-full rounded-[24px] border border-slate-200 bg-slate-950 px-4 py-4 font-mono text-xs leading-6 text-slate-100 outline-none focus:border-brand"
              />
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={handleSaveHtmlOverride}
                  disabled={action !== null}
                  className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {action === "save-html" ? "Saving..." : "Save HTML Override"}
                </button>
                {draftState.html_override ? (
                  <button
                    type="button"
                    onClick={handleDiscardHtmlOverride}
                    disabled={action !== null}
                    className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {action === "discard-html" ? "Discarding..." : "Discard Override"}
                  </button>
                ) : null}
              </div>
            </>
          ) : null}
        </div>
      </section>

      <aside className="space-y-6">
        <SubjectLinePicker options={structure.subject_lines} selected={selectedSubjectLine} onSelect={setSelectedSubjectLine} />
        <PreviewTabs html={activePreviewHtml} mjml={draftState.preview_mjml} />
      </aside>
    </div>
  );
}
