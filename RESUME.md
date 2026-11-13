# Resuming Data-Driven Daily

Repository: https://github.com/smcox13/data-driven-daily

## Restore and run locally

```sh
git clone https://github.com/smcox13/data-driven-daily.git
cd data-driven-daily
conda env create -f environment.yml
conda activate data-driven-daily
npm ci
cp .env.example apps/api/.env
cp .env.example apps/web/.env.local
```

Edit `apps/api/.env`: set `DATABASE_URL=sqlite:///./data_driven_daily.db`
to use the database preserved in this repository. Add your own OpenAI API key
if using AI features. The API reads `.env` relative to its working directory.

Edit `apps/web/.env.local`: set `DEV_LOGIN_BYPASS=true` for local development
without Google OAuth, and set `NEXTAUTH_SECRET` to a newly generated random value.
For Google sign-in, supply your Google client ID and secret instead.
Keep `JWT_SHARED_SECRET` consistent wherever configured. Never commit real credentials.

Start the API in one terminal:

```sh
conda activate data-driven-daily
cd apps/api
uvicorn app.main:app --reload
```

Start the frontend in another terminal from the repository root:

```sh
conda activate data-driven-daily
npm run dev:web
```

Open http://localhost:3000. API health is at http://localhost:8000/health.
To run backend tests, install the development extra with
`python -m pip install -e 'apps/api[dev]'`, then run `python -m pytest apps/api/tests`.

For Postgres and Redis instead, run `docker compose up -d postgres redis` and
use the Postgres URL in `.env.example`. This creates a separate database;
it does not import the tracked SQLite data automatically.

## Preservation audit — November 13, 2026

- The source, npm lockfile, Conda environment specification, Docker configuration,
  and `apps/api/data_driven_daily.db` are tracked. SQLite integrity check returned `ok`.
- No local credential files were found in the project. `.env.example` contains
  placeholders; credentials must be supplied again when resuming.
- The only ignored files found were dependencies, generated builds, Python/test
  caches, and macOS metadata. Recreate dependencies with the commands above.
- There were no additional local branches or stashes to preserve.
- Docker was unavailable because its daemon was not running. Any existing Docker
  Postgres volume remains unverified. Preserve/export it separately before deleting
  Docker data or uninstalling Docker if it contains work you need.
- Existing tracked `.next.bak-*` build output and Python package metadata were
  retained as-is. They are not required to reinstall the project.
- This audit verifies preservation, not application runtime or build health.

The local project folder has deliberately not been deleted. Once the pushed
commit is verified, the repository can be cloned again using the steps above.
