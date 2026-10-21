# Carpeta `services`

Esta carpeta contiene **todos los servicios backend** (APIs y workers en segundo plano) relacionados con la compañía para el proyecto transversal de AI Engineering.

Cada subcarpeta dentro de `services/` debe corresponder a **un servicio concreto** (por ejemplo `admin-api`, `data-processor-worker`) e incluir su propia documentación técnica y funcional.

- **Propósito principal**: centralizar toda la lógica backend, APIs y consumidores de colas que dan soporte a los casos de uso de la compañía.
- **Recomendación**: documenta en este archivo (o en sub-READMEs) los servicios que vayas añadiendo, su objetivo, tecnología usada y cómo ejecutarlos.

## Ejecutar el stack con Docker

Existen dos archivos de ejemplo distintos; no son intercambiables:

| Archivo | Lo usa |
| ------- | ------ |
| `.env.example` (raíz del repo) | `docker compose` (`env_file: .env` en `docker-compose.yml`) |
| `services/api/.env.example` | Ejecución directa de la API (`uvicorn` desde `services/api`) |

```bash
cp .env.example .env        # editar JWT_SECRET; DATABASE_URL por defecto es SQLite
docker compose up --build   # API :8000, website :3000, backoffice :3001
```

Los archivos `.env` están ignorados por Git; nunca se versionan. Para Supabase, define `DATABASE_URL` en `.env`.

## Pruebas de la API

Las pruebas usan una base SQLite temporal y datos TinyDB temporales (`API_DATA_DIR`); nunca leen
`services/api/.env` ni `services/api/data/`.

```bash
cd services/api && uv sync && uv run pytest
```

Las pruebas `xfail` documentan defectos conocidos aún abiertos (ver cada `reason`).
