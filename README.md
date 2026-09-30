# BotanicalBuddy

Plant-care assistant: a Nuxt 3 / Vuetify frontend (`frontend/`) and a Django REST
backend (`botanicalbuddy/`) backed by PostgreSQL + pgvector and an LLM (OpenAI or Ollama).

## Prerequisites

| Tool | Version |
| --- | --- |
| Node.js | 22 (`frontend/.nvmrc`; >= 20.11 works) |
| Yarn | 1.22 (classic) |
| Python | 3.12 (`botanicalbuddy/.python-version`; also verified on 3.11) |
| PostgreSQL | 16 with the `pgvector` extension (Docker Compose file provided) |

## Run locally

### 1. Database

```bash
docker compose up -d db          # pgvector/pgvector:pg16 on 127.0.0.1:5432
```

Set `DATABASE_PORT` (shell or root `.env`) if 5432 is taken. Or use your own
PostgreSQL with pgvector installed; the initial migration runs `CREATE EXTENSION vector`.

### 2. Backend (http://localhost:8000)

```bash
cd botanicalbuddy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt   # includes the spaCy en_core_web_sm model
cp .env.example .env                                  # then edit the placeholders
python manage.py migrate
python manage.py runserver 8000
```

### 3. Frontend (http://localhost:3000)

```bash
cd frontend
yarn install --frozen-lockfile
cp .env.example .env                                  # then edit the placeholders
yarn dev
```

The frontend proxies `/api`, `/session` and `/login` to `http://localhost:8000`,
so pages that check the session return 502 until the backend is running.

## Checks

```bash
# frontend
cd frontend && yarn typecheck && yarn build

# backend (needs the database above)
cd botanicalbuddy
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

There is no linter configured for either side yet.

## Known gaps

- `AUTH_USER_MODEL` is unset (Django's `auth.User`) while the models reference
  `backend.User`; endpoints that use `request.user.conversations` need that decided.
- Several views are `async def` under DRF's `@api_view`; DRF 3.15 has no async view support, and these views (`ask`, `upload_image`, `messages`) are not covered by tests.
- `upload_image` posts to a placeholder model-API URL.
- `load_trefel_data.py` requires `TREFLE_API_KEY` and calls the live Trefle API.
