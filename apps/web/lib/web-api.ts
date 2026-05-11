import type { Draft, DraftGenerateInput, ExportResponse } from "@/lib/types";

type JsonBody = Record<string, unknown>;

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {})
    }
  });

  const text = await response.text();
  const body = text ? (JSON.parse(text) as JsonBody) : {};

  if (!response.ok) {
    const detail = typeof body.detail === "string" ? body.detail : `Request failed with status ${response.status}`;
    throw new Error(detail);
  }

  return body as T;
}

export function createDraft(payload: DraftGenerateInput) {
  return requestJson<Draft>("/api/drafts", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateDraft(draftId: string, payload: JsonBody) {
  return requestJson<Draft>(`/api/drafts/${draftId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function regenerateDraftContent(draftId: string, payload: JsonBody) {
  return requestJson<Draft>(`/api/drafts/${draftId}/regenerate`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function saveHtmlOverride(draftId: string, html: string) {
  return requestJson<Draft>(`/api/drafts/${draftId}/html-override`, {
    method: "POST",
    body: JSON.stringify({ html })
  });
}

export function discardHtmlOverride(draftId: string) {
  return requestJson<Draft>(`/api/drafts/${draftId}/html-override`, {
    method: "DELETE"
  });
}

export function exportDraft(draftId: string) {
  return requestJson<ExportResponse>(`/api/exports/${draftId}`, {
    method: "POST"
  });
}
