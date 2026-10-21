# `services` folder

This folder contains **all the backend services** (APIs and background workers) related to the company for the cross-functional AI Engineering project.

Each subfolder inside `services/` must correspond to **one specific service** (for example: `admin-api`, `data-processor-worker`) and include its own technical and functional documentation.

- **Main purpose**: to centralize all the backend logic, APIs, and queue consumers that support the company's use cases.
- **Recommendation**: document in this file (or in sub-READMEs) the services you add, their objective, the technology used, and how to run them.

> _Spanish version: [README.es.md](./README.es.md)._

## Run the stack with Docker

Two different example files exist; they are not interchangeable:

| File | Used by |
| ---- | ------- |
| `.env.example` (repo root) | `docker compose` (`env_file: .env` in `docker-compose.yml`) |
| `services/api/.env.example` | Running the API directly (`uvicorn` from `services/api`) |

```bash
cp .env.example .env        # edit JWT_SECRET; the default DATABASE_URL is SQLite
docker compose up --build   # API :8000, website :3000, backoffice :3001
```

`.env` files are git-ignored; never commit them. For Supabase, set `DATABASE_URL` in `.env`.

## API tests

Tests use a temporary SQLite database and temporary TinyDB data (`API_DATA_DIR`); they never read
`services/api/.env` or `services/api/data/`.

```bash
cd services/api && uv sync && uv run pytest
```

`xfail` tests document known defects that are still open (see each `reason`).

## Incident analysis results: scope and limitations

- `POST /api/incidents/analyze` and `GET /api/incidents/results/{summary,categories,export}` require a
  valid JWT. Results are stored **per user**; a user can only read or export their own (404 if none).
- A failed upload (invalid CSV, truncated rows, extra columns, no records) returns 400 and keeps the
  previous analysis.
- Results are **temporary**: kept in process memory (`results_store.py`), lost on restart, and not
  evicted while the process lives (one entry per user).
- The cache (`cache.py`, TTL 60 s) is keyed by `user:version:name`. Each analysis gets a new version, so a
  computation that finishes after a newer upload cannot publish obsolete data.
- **Multiple processes:** results and cache are per process. With several workers or replicas a user
  may be routed to a process that has no analysis (404) or an older one. Use a single worker, sticky
  routing, or move results/cache to a shared store (e.g. Redis or a table) before scaling out.
- TinyDB (users, suppliers, incidents) is serialized by a lock **inside one process** only; it must not
  be shared by several processes.
- The inventory API (`/inventory/*`) requires authentication on every route; there are no roles yet.
