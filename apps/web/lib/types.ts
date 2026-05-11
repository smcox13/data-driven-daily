export type Category = {
  id: string;
  name: string;
  slug: string;
};

export type Source = {
  id: string;
  name: string;
  url: string;
  type: string;
  enabled: boolean;
  category_id?: string | null;
  authority_score: number;
  notes?: string | null;
};

export type Article = {
  id: string;
  title: string;
  url: string;
  canonical_url: string;
  author?: string | null;
  publish_date?: string | null;
  excerpt?: string | null;
  topic?: string | null;
  ranking_score: number;
  popularity_score: number;
  ai_relevance_score: number;
  editor_preference_score: number;
  source_authority_score: number;
  is_suppressed: boolean;
  category_id?: string | null;
};

export type DraftStructure = {
  issue_date: string;
  featured_insight: {
    article_id: string;
    title: string;
    url: string;
    summary: string;
  };
  quick_hits: Array<{
    article_id: string;
    title: string;
    url: string;
    summary: string;
  }>;
  tldr: string;
  cta: {
    headline: string;
    body: string;
  };
  footer: {
    brand: string;
    disclaimer: string;
  };
  subject_lines: string[];
};

export type Draft = {
  id: string;
  issue_date: string;
  status: string;
  title: string;
  selected_subject_line?: string | null;
  preheader?: string | null;
  structure_json: DraftStructure;
  preview_html?: string | null;
  preview_mjml?: string | null;
  html_override?: string | null;
  generation_metadata: Record<string, unknown>;
  ai_provider: string;
  model_map: Record<string, string>;
  created_at: string;
  updated_at: string;
};

export type DraftGenerateInput = {
  issue_date: string;
  quick_hit_count: number;
  category_ids: string[];
};

export type NewsletterSnapshot = {
  id: string;
  draft_id: string;
  issue_date: string;
  subject_line: string;
  html: string;
  mjml?: string | null;
  snapshot_json: DraftStructure;
  export_metadata: Record<string, unknown>;
  created_at: string;
};

export type AiProviderConfig = {
  id: string;
  provider: string;
  enabled: boolean;
  is_active: boolean;
  prompt_version: string;
  api_base?: string | null;
  model_overrides: Record<string, string>;
  created_at: string;
  updated_at: string;
};

export type AiTaskConfig = {
  id: string;
  task_type: string;
  model: string;
  temperature: number;
  max_tokens: number;
  prompt_version: string;
  extra_config: Record<string, unknown>;
};

export type AiSettings = {
  active_provider: string;
  providers: AiProviderConfig[];
  task_configs: AiTaskConfig[];
};

export type ExportResponse = {
  snapshot: NewsletterSnapshot;
  mailchimp_html: string;
};
