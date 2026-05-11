import { getAiSettings } from "@/lib/api";

export default async function AiSettingsPage() {
  const settings = await getAiSettings();

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">AI Provider Control</p>
        <h2 className="mt-2 text-3xl font-semibold text-ink">OpenAI is live, Gemini is staged for cutover</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate">
          Provider selection, task-level model mapping, and prompt versions live here so the eventual Gemini switch does not force
          schema or workflow changes elsewhere in the app.
        </p>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Providers</p>
          <div className="mt-5 space-y-4">
            {settings.providers.map((provider) => (
              <div key={provider.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-ink">{provider.provider}</h3>
                    <p className="mt-1 text-sm text-slate">Prompt version: {provider.prompt_version}</p>
                  </div>
                  <span className={`rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] ${provider.is_active ? "bg-brand/10 text-brand" : "bg-slate-100 text-slate"}`}>
                    {provider.is_active ? "Active" : provider.enabled ? "Ready" : "Disabled"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[28px] border border-white/70 bg-white/95 p-6 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Task Models</p>
          <div className="mt-5 space-y-4">
            {settings.task_configs.map((task) => (
              <div key={task.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="text-sm font-semibold uppercase tracking-[0.16em] text-brand">{task.task_type}</div>
                    <div className="mt-2 text-lg font-semibold text-ink">{task.model}</div>
                  </div>
                  <div className="text-sm text-slate">
                    <div>Temp: {task.temperature}</div>
                    <div>Max tokens: {task.max_tokens}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

