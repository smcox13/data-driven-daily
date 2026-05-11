import Link from "next/link";
import { BarChart3, BookOpenText, Bot, Newspaper, Rss, Settings2 } from "lucide-react";
import type { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/sources", label: "Sources", icon: Rss },
  { href: "/articles", label: "Article Library", icon: BookOpenText },
  { href: "/drafts", label: "Drafts", icon: Bot },
  { href: "/newsletters", label: "Archive", icon: Newspaper },
  { href: "/settings/ai", label: "AI Settings", icon: Settings2 }
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
            {navItems.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium text-slate transition hover:bg-mist hover:text-ink"
              >
                <Icon className="h-4 w-4" />
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
