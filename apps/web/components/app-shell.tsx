import Link from "next/link";
import type { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Dashboard", marker: "DB" },
  { href: "/sources", label: "Sources", marker: "RS" },
  { href: "/articles", label: "Article Library", marker: "AR" },
  { href: "/drafts", label: "Drafts", marker: "AI" },
  { href: "/newsletters", label: "Archive", marker: "NL" },
  { href: "/settings/ai", label: "AI Settings", marker: "ST" }
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(15,118,110,0.18),_transparent_30%),linear-gradient(180deg,#f8fafc_0%,#eef2f7_100%)] text-ink">
      <div className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-8 px-4 py-6 lg:grid-cols-[260px_1fr] lg:px-6">
        <aside className="rounded-[28px] border border-white/60 bg-white/80 p-6 shadow-panel backdrop-blur">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-brand">Editorial Command</p>
            <h1 className="mt-3 font-serif text-3xl leading-tight">Data-Driven Daily</h1>
            <p className="mt-3 text-sm leading-6 text-slate">
              Generate, curate, preview, and export executive newsletters without losing editorial control.
            </p>
          </div>

          <nav className="space-y-2">
            {navItems.map(({ href, label, marker }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium text-slate transition hover:bg-mist hover:text-ink"
              >
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-[10px] font-semibold tracking-[0.12em] text-brand">
                  {marker}
                </span>
                {label}
              </Link>
            ))}
          </nav>

          <div className="mt-8 rounded-2xl bg-ink p-4 text-sm text-slate-100">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Workflow target</p>
            <p className="mt-2 font-medium text-white">Draft to export in under 15 minutes</p>
          </div>
        </aside>

        <main className="pb-10">{children}</main>
      </div>
    </div>
  );
}
