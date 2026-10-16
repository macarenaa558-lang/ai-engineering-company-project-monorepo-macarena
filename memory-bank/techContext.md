# Brasaland — Contexto técnico

## Arquitectura
El proyecto utiliza el monorepositorio existente de Brasaland Digital.

## Ubicación de aplicaciones
- `uis/website/`: ubicación prevista para el sitio web corporativo público; actualmente no existe en esta rama.
- `uis/backoffice/`: aplicación interna de gestión.
- `services/`: servicios y APIs.
- `services/api/`: API backend existente.

## Tecnologías utilizadas
El repositorio contiene desarrollos con React, TypeScript, Python y FastAPI.

Antes de modificar una aplicación, verificar sus dependencias y configuración en los archivos correspondientes.

## Decisiones arquitectónicas
- Reutilizar las aplicaciones existentes.
- Evitar crear proyectos paralelos innecesarios.
- Mantener separados frontend, backend y documentación.
- Respetar las convenciones del repositorio.
- Documentar cambios importantes antes de implementarlos.

## Restricciones
- No modificar credenciales ni archivos `.env`.
- No alterar bases de datos sin autorización.
- No modificar aplicaciones fuera del alcance solicitado.
- Considerar las operaciones en Colombia y Florida.
