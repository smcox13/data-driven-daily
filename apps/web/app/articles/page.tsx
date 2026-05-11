import { ArticleLibrary } from "@/components/article-library";
import { getArticles } from "@/lib/api";

export default async function ArticlesPage() {
  const articles = await getArticles();

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Ranked Inventory</p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">Search, filter, and replace without losing velocity</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate">
          Suppressed duplicates remain searchable here. This screen is designed to support remove-and-replace workflows during the
          editorial pass, not just passive article browsing.
        </p>
      </section>

      <ArticleLibrary articles={articles} />
    </div>
  );
}

