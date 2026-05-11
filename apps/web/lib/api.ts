import { backendJson, BackendRequestError } from "@/lib/backend-api";
import { mockAiSettings, mockArticles, mockDraft, mockNewsletters, mockSources } from "@/lib/mock-data";
import type { AiSettings, Article, Draft, NewsletterSnapshot, Source } from "@/lib/types";

export async function getSources(): Promise<Source[]> {
  try {
    return await backendJson<Source[]>("/sources");
  } catch {
    return mockSources;
  }
}

export async function getArticles(): Promise<Article[]> {
  try {
    const payload = await backendJson<{ items: Article[] }>("/articles");
    return payload.items;
  } catch {
    return mockArticles;
  }
}

export async function getDraft(draftId: string): Promise<Draft | null> {
  try {
    return await backendJson<Draft>(`/drafts/${draftId}`);
  } catch (error) {
    if (error instanceof BackendRequestError && error.status === 404) {
      return null;
    }
    return mockDraft;
  }
}

export async function getDrafts(): Promise<Draft[]> {
  try {
    return await backendJson<Draft[]>("/drafts");
  } catch {
    return [mockDraft];
  }
}

export async function getNewsletters(): Promise<NewsletterSnapshot[]> {
  try {
    return await backendJson<NewsletterSnapshot[]>("/newsletters");
  } catch {
    return mockNewsletters;
  }
}

export async function getAiSettings(): Promise<AiSettings> {
  try {
    return await backendJson<AiSettings>("/ai/settings");
  } catch {
    return mockAiSettings;
  }
}
