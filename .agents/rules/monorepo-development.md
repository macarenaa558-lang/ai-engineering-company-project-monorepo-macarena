# Regla de desarrollo — Brasaland

## Alcance
Always apply — esta regla se aplica a todas las tareas y archivos del monorepositorio.

## Reglas
1. Leer `CONTEXT.md` y `memory-bank/` antes de modificar código.
2. Respetar la estructura existente:
   - `uis/website/`: ubicación prevista para el sitio corporativo; actualmente no existe en esta rama.
   - `uis/backoffice/`: aplicación interna.
   - `services/`: APIs y servicios.
3. No crear aplicaciones paralelas.
4. Mantener los cambios limitados a la tarea solicitada.
5. No modificar archivos `.env`, credenciales ni datos sensibles.
6. Solicitar autorización antes de cambiar infraestructura, dependencias o bases de datos.
7. Ejecutar las validaciones disponibles antes de cada commit.
8. Actualizar `memory-bank/progress.md` cuando cambie el estado del proyecto.

## Consideraciones empresariales
Las soluciones deben respetar las necesidades de Brasaland, sus 14 restaurantes y sus operaciones en Colombia y Florida.
