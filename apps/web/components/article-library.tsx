"use client";

import { useState } from "react";

import type { Article } from "@/lib/types";

type ArticleLibraryProps = {
  articles: Article[];
};

export function ArticleLibrary({ articles }: ArticleLibraryProps) {
  const [query, setQuery] = useState("");

  const normalized = query.toLowerCase().trim();
  const filtered = normalized
    ? articles.filter((article) => {
        return [article.title, article.excerpt ?? "", article.author ?? "", article.topic ?? ""]
          .join(" ")
          .toLowerCase()
          .includes(normalized);
      })
    : articles;

  return (
    <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Article Library</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Search replacement candidates fast</h2>
        </div>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by keyword, author, topic..."
          className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-brand lg:max-w-sm"
        />
      </div>
      <div className="mt-6 space-y-4">
        {filtered.map((article) => (
          <article key={article.id} className="rounded-2xl border border-slate-200 p-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <a href={article.url} className="text-lg font-semibold text-ink underline decoration-brand/30 underline-offset-4">
                  {article.title}
                </a>
                <p className="mt-2 text-sm leading-6 text-slate">{article.excerpt}</p>
              </div>
              <div className="rounded-2xl bg-mist px-4 py-3 text-sm text-slate">
                <div>Rank: {article.ranking_score.toFixed(2)}</div>
                <div>AI: {article.ai_relevance_score.toFixed(2)}</div>
                <div>Source: {article.source_authority_score.toFixed(2)}</div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
