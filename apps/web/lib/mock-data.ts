import type { AiSettings, Article, Draft, NewsletterSnapshot, Source } from "@/lib/types";

export const mockSources: Source[] = [
  {
    id: "source-1",
    name: "MarTech",
    url: "https://martech.org/feed/",
    type: "rss",
    enabled: true,
    category_id: "cat-martech",
    authority_score: 0.86,
    notes: "Strong signal for daily marketing technology coverage."
  },
  {
    id: "source-2",
    name: "Marketing Brew",
    url: "https://www.marketingbrew.com/feed",
    type: "rss",
    enabled: true,
    category_id: "cat-email",
    authority_score: 0.75,
    notes: "Useful for trend scanning and campaign shifts."
  }
];

export const mockArticles: Article[] = [
  {
    id: "article-1",
    title: "Retail media budgets shift toward first-party measurement stacks",
    url: "https://example.com/article-1",
    canonical_url: "https://example.com/article-1",
    author: "Jordan Lee",
    publish_date: "2026-05-11",
    excerpt: "Brands are reallocating budget toward measurement layers that unify retail media, CRM, and incrementality reporting.",
    topic: "retail media measurement budget",
    ranking_score: 0.93,
    popularity_score: 0.0,
    ai_relevance_score: 0.89,
    editor_preference_score: 0.21,
    source_authority_score: 0.82,
    is_suppressed: false,
    category_id: "cat-crm"
  },
  {
    id: "article-2",
    title: "Privacy rule changes force martech vendors to rework identity workflows",
    url: "https://example.com/article-2",
    canonical_url: "https://example.com/article-2",
    author: "Avery Patel",
    publish_date: "2026-05-11",
    excerpt: "Identity orchestration vendors are adapting consent flows and enrichment pipelines to stay compliant.",
    topic: "privacy consent identity workflows",
    ranking_score: 0.88,
    popularity_score: 0.0,
    ai_relevance_score: 0.87,
    editor_preference_score: 0.19,
    source_authority_score: 0.8,
    is_suppressed: false,
    category_id: "cat-privacy"
  },
  {
    id: "article-3",
    title: "AI copilots are moving from dashboard summaries into campaign operations",
    url: "https://example.com/article-3",
    canonical_url: "https://example.com/article-3",
    author: "Samir Chen",
    publish_date: "2026-05-10",
    excerpt: "Teams are pushing AI assistants closer to briefing, segmentation, and optimization workflows.",
    topic: "ai copilots campaign operations",
    ranking_score: 0.84,
    popularity_score: 0.0,
    ai_relevance_score: 0.83,
    editor_preference_score: 0.11,
    source_authority_score: 0.78,
    is_suppressed: false,
    category_id: "cat-ai"
  }
];

export const mockDraft: Draft = {
  id: "draft-1",
  issue_date: "2026-05-11",
  status: "draft",
  title: "Data-Driven Daily | 2026-05-11",
  selected_subject_line: "Retail media, privacy, and AI workflow shifts to watch",
  preheader: "Executive intelligence for data, AI, martech, and measurement leaders.",
  structure_json: {
    issue_date: "2026-05-11",
    featured_insight: {
      article_id: "article-1",
      title: "Retail media budgets shift toward first-party measurement stacks",
      url: "https://example.com/article-1",
      summary:
        "What happened: brands are reallocating retail media budget toward measurement layers that connect CRM, incrementality, and channel performance. Why it matters: this shifts differentiation away from media buying alone and toward measurement infrastructure. Impact: marketing and analytics leaders will need cleaner data contracts and more credible attribution narratives."
    },
    quick_hits: [
      {
        article_id: "article-2",
        title: "Privacy rule changes force martech vendors to rework identity workflows",
        url: "https://example.com/article-2",
        summary:
          "Consent, identity resolution, and enrichment workflows are being redesigned as privacy constraints tighten. Leaders should expect vendor evaluations to focus more heavily on auditability and data lineage."
      },
      {
        article_id: "article-3",
        title: "AI copilots are moving from dashboard summaries into campaign operations",
        url: "https://example.com/article-3",
        summary:
          "AI assistants are expanding from passive reporting into operational decision support. The strategic question is no longer whether to use copilots, but where human approvals remain non-negotiable."
      }
    ],
    tldr:
      "Measurement quality is becoming the control point for retail media effectiveness, privacy shifts are rewriting identity workflows, and AI assistants are moving into day-to-day campaign execution.",
    cta: {
      headline: "Data Corner",
      body: "Use this issue to stress-test how ready your team is for measurement-centric planning, privacy-safe orchestration, and operational AI."
    },
    footer: {
      brand: "Data-Driven Daily",
      disclaimer: "Prepared for editorial review. Validate facts before distribution."
    },
    subject_lines: [
      "Retail media, privacy, and AI workflow shifts to watch",
      "What data and marketing leaders need to adjust this week",
      "Three strategic signals shaping analytics and martech execution"
    ]
  },
  preview_html: "<html><body><h1>Preview placeholder</h1></body></html>",
  preview_mjml: "<mjml><mj-body><mj-section><mj-column><mj-text>Preview</mj-text></mj-column></mj-section></mj-body></mjml>",
  html_override: null,
  generation_metadata: {
    provider: "openai",
    usage: {
      summaries: {},
      tldr: {},
      subject: {}
    }
  },
  ai_provider: "openai",
  model_map: {
    default: "gpt-4.1"
  },
  created_at: "2026-05-11T12:00:00Z",
  updated_at: "2026-05-11T12:10:00Z"
};

export const mockNewsletters: NewsletterSnapshot[] = [
  {
    id: "snapshot-1",
    draft_id: "draft-1",
    issue_date: "2026-05-11",
    subject_line: "Retail media, privacy, and AI workflow shifts to watch",
    html: "<html><body><h1>Snapshot</h1></body></html>",
    mjml: null,
    snapshot_json: mockDraft.structure_json,
    export_metadata: {
      format: "mailchimp_html"
    },
    created_at: "2026-05-11T12:30:00Z"
  }
];

export const mockAiSettings: AiSettings = {
  active_provider: "openai",
  providers: [
    {
      id: "provider-1",
      provider: "openai",
      enabled: true,
      is_active: true,
      prompt_version: "v1",
      api_base: null,
      model_overrides: {
        summary: "gpt-4.1",
        relevance: "gpt-4.1-mini",
        subject: "gpt-4.1-mini",
        tldr: "gpt-4.1-mini"
      },
      created_at: "2026-05-11T10:00:00Z",
      updated_at: "2026-05-11T10:00:00Z"
    },
    {
      id: "provider-2",
      provider: "gemini",
      enabled: false,
      is_active: false,
      prompt_version: "v1",
      api_base: null,
      model_overrides: {},
      created_at: "2026-05-11T10:00:00Z",
      updated_at: "2026-05-11T10:00:00Z"
    }
  ],
  task_configs: [
    {
      id: "task-1",
      task_type: "summary",
      model: "gpt-4.1",
      temperature: 0.2,
      max_tokens: 900,
      prompt_version: "v1",
      extra_config: {}
    },
    {
      id: "task-2",
      task_type: "subject",
      model: "gpt-4.1-mini",
      temperature: 0.2,
      max_tokens: 500,
      prompt_version: "v1",
      extra_config: {}
    }
  ]
};

