"use client";

import { useState } from "react";

type PreviewTabsProps = {
  html: string;
  mjml?: string | null;
};

export function PreviewTabs({ html, mjml }: PreviewTabsProps) {
  const [activeTab, setActiveTab] = useState<"desktop" | "mobile" | "code">("desktop");

  return (
    <div className="rounded-[28px] border border-white/70 bg-white/95 p-5 shadow-panel">
      <div className="mb-4 flex flex-wrap gap-2">
        {[
          { value: "desktop", label: "Desktop Preview" },
          { value: "mobile", label: "Mobile Preview" },
          { value: "code", label: "MJML / HTML" }
        ].map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => setActiveTab(tab.value as "desktop" | "mobile" | "code")}
            className={`rounded-full px-4 py-2 text-sm font-medium ${
              activeTab === tab.value ? "bg-ink text-white" : "bg-mist text-slate"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "code" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <pre className="overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">{mjml ?? "MJML unavailable"}</pre>
          <pre className="overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">{html}</pre>
        </div>
      ) : (
        <div className={`mx-auto overflow-hidden rounded-[24px] border border-slate-200 bg-white ${activeTab === "mobile" ? "max-w-sm" : "max-w-4xl"}`}>
          <iframe
            title={`${activeTab} preview`}
            className="h-[780px] w-full bg-white"
            srcDoc={html}
          />
        </div>
      )}
    </div>
  );
}

