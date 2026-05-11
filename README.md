# Data-Driven Daily

Data-Driven Daily is a greenfield AI-assisted executive newsletter platform built around human editorial control, fast curation, and HTML export for ESPs such as Mailchimp.

## Repo layout

- `apps/api`: FastAPI-based backend, AI orchestration, article ingestion, ranking, draft generation, export, and archive services.
- `apps/web`: Next.js editorial UI with Google auth, structured newsletter editing, previews, and AI settings.

## What is implemented

- Single-organization application scaffolding with org-aware models and API contracts.
- Article/source/category management, duplicate suppression logic, ranking, and editor feedback aggregation.
- OpenAI-first provider abstraction with Gemini-ready config surface.
- Structured newsletter draft model, HTML override flow, MJML source generation, HTML rendering fallback, immutable snapshot export, and archive APIs.
- Next.js dashboard, source/article/newsletter screens, draft editor UI, and AI settings surface.

## Local development

### Recommended environment

1. Create the project Conda environment with `conda env create -f environment.yml`.
2. Activate it with `conda activate data-driven-daily`.
3. For local UI testing without Google OAuth, set `DEV_LOGIN_BYPASS=true` in your env file or run the dev server with dummy Google credentials.

### Backend

1. Activate the Conda environment.
2. Run `uvicorn app.main:app --reload` from `apps/api`.

### Frontend

1. Activate the Conda environment.
2. Run `npm install`.
3. Run `npm run dev:web`.

### Infrastructure

Run `docker compose up postgres redis` to start Postgres with `pgvector` and Redis.

## Notes

- The backend includes an HTML renderer fallback when the MJML CLI is unavailable locally.
- The frontend is scaffolded against Next.js and Auth.js, but this environment does not currently include a Node toolchain, so it has not been executed here.
- `ALLOW_DEMO_AUTH=true` allows the API to operate with a seeded local editor when auth is not wired end to end yet.
