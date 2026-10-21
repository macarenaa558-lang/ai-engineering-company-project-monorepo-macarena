# AGENTS.md — Brasaland Digital

## Objetivo
Guiar a los agentes de inteligencia artificial que trabajan en el monorepositorio de Brasaland, respetando el contexto empresarial, la arquitectura y las convenciones existentes.

## Lectura obligatoria al iniciar
Antes de modificar archivos, el agente debe leer en este orden:

1. `CONTEXT.md` — contexto empresarial de Brasaland.
2. `memory-bank/projectbrief.md` — objetivos y necesidades del negocio.
3. `memory-bank/techContext.md` — arquitectura y restricciones técnicas.
4. `memory-bank/progress.md` — estado actual y próximos pasos.
5. Las reglas aplicables de `.agents/rules/`.
6. El README del módulo que se va a modificar.

## Estructura del monorepositorio
- `uis/website/`: ubicación prevista para el sitio web corporativo público; actualmente no existe en esta rama.
- `uis/backoffice/`: aplicación interna.
- `services/`: servicios y APIs.
- `services/api/`: backend existente.

No crear aplicaciones paralelas cuando ya exista un módulo adecuado.

## Flujo obligatorio antes de cada commit
1. Leer el contexto empresarial y el banco de memoria.
2. Identificar el módulo afectado y revisar sus instrucciones.
3. Definir el alcance del cambio y comprobar las reglas aplicables.
4. Implementar únicamente los cambios solicitados.
5. Ejecutar las validaciones disponibles para los archivos modificados.
6. Revisar `git diff` y `git status` para detectar cambios inesperados.
7. Actualizar `memory-bank/progress.md` si corresponde.
8. Realizar el commit con un mensaje descriptivo en español.

## Convenciones
- Mantener la estructura existente del monorepositorio.
- Respetar los nombres, formatos y tecnologías de cada módulo.
- Evitar cambios que no estén relacionados con la tarea.
- Documentar decisiones técnicas importantes.
- Priorizar soluciones reutilizables y fáciles de mantener.

## Cambios que requieren autorización explícita
- Modificar o eliminar bases de datos.
- Cambiar credenciales, secretos o archivos `.env`.
- Eliminar módulos o archivos existentes.
- Modificar infraestructura o configuraciones de despliegue.
- Incorporar dependencias nuevas.
- Alterar funcionalidades fuera del alcance solicitado.

## Seguridad
Nunca incluir secretos, credenciales ni datos sensibles en commits.

## Finalización
Antes de entregar, comprobar que se cumplan los criterios de aceptación, que las validaciones hayan terminado y que el Pull Request contenga únicamente los cambios previstos.
