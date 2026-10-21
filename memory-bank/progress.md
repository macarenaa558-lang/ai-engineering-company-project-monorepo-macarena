# Brasaland — Progreso

## Estado actual
La rama `integration/full-monorepo` reúne autenticación, proveedores, inventario, gestor y análisis de incidencias, caché, backoffice, website y Docker. Está verificada localmente (pytest con SQLite y PostgreSQL local, frontend, Docker y navegador). No se ha publicado.

## Completado
- Integración de todas las ramas de funcionalidades sobre `feature/serialization-audit`.
- Análisis de incidencias y sus resultados con autenticación, separados por usuario y con caché versionada.
- Validación de CSV truncados y porcentajes sin división entre cero (API y CLI).
- Inventario con autenticación en todas las rutas y enlace en el menú del backoffice.
- `services.py` renombrado a `repository.py` (colisión con el paquete `services`).
- `.env.example` en la raíz para Docker Compose y pruebas con datos aislados.

## Pendiente
- Verificar contra Supabase con credenciales de prueba (no se ha usado la base real).
- Resultados y caché son por proceso: usar un solo worker o un almacén compartido antes de escalar.
- TinyDB no debe compartirse entre procesos.
- Publicar la rama y abrir el Pull Request cuando se autorice.
