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
