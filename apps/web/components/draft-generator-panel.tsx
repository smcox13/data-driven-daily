"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createDraft } from "@/lib/web-api";

type DraftGeneratorPanelProps = {
  className?: string;
};

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function DraftGeneratorPanel({ className }: DraftGeneratorPanelProps) {
  const router = useRouter();
  const [issueDate, setIssueDate] = useState(todayIso());
  const [quickHitCount, setQuickHitCount] = useState(3);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setIsSubmitting(true);
    setError(null);
    try {
      const draft = await createDraft({
        issue_date: issueDate,
        quick_hit_count: quickHitCount,
        category_ids: []
      });
      router.push(`/drafts/${draft.id}`);
      router.refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to generate draft.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className={`rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel ${className ?? ""}`}>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Generate Draft</p>
          <h3 className="mt-2 text-2xl font-semibold text-ink">Kick off a fresh issue from the ranked article pool</h3>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-slate">
            Local demo content is pre-seeded, so you can generate a working issue immediately and then edit or export it from the UI.
          </p>
        </div>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={isSubmitting}
          className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Generating..." : "Generate Draft"}
        </button>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Issue date</span>
          <input
            type="date"
            value={issueDate}
            onChange={(event) => setIssueDate(event.target.value)}
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-ink outline-none focus:border-brand"
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Quick hits</span>
          <select
            value={quickHitCount}
            onChange={(event) => setQuickHitCount(Number(event.target.value))}
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-ink outline-none focus:border-brand"
          >
            {[3, 4, 5, 6, 7, 8, 9].map((count) => (
              <option key={count} value={count}>
                {count}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error ? <p className="mt-4 rounded-2xl bg-red-50 px-4 py-3 text-sm text-danger">{error}</p> : null}
    </div>
  );
}

