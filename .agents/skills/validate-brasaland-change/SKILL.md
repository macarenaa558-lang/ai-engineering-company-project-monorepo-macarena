# Skill — Validar cambios de Brasaland

## Objetivo
Verificar que un cambio en el monorepositorio respete el contexto empresarial, la arquitectura y las reglas de desarrollo antes de realizar un commit.

## Cuándo utilizarla
Antes de confirmar cambios o preparar un Pull Request.

## Entradas
- Descripción de la tarea solicitada.
- Archivos modificados.
- `CONTEXT.md`.
- `AGENTS.md`.
- Archivos de `memory-bank/`.
- Reglas de `.agents/rules/`.
- README del módulo afectado.

## Procedimiento
1. Leer el contexto y las instrucciones del proyecto.
2. Identificar los archivos modificados con `git status`.
3. Revisar las diferencias con `git diff`.
4. Comprobar que los cambios pertenecen al módulo correcto.
5. Detectar modificaciones fuera del alcance.
6. Verificar que no se incluyan secretos ni archivos `.env`.
7. Ejecutar las pruebas o validaciones disponibles.
8. Informar los resultados y posibles problemas.

## Criterios de aceptación
- [ ] Los cambios responden a la tarea solicitada.
- [ ] Se respeta la estructura existente del monorepositorio.
- [ ] No existen aplicaciones paralelas innecesarias.
- [ ] No se incluyen credenciales ni información sensible.
- [ ] Las validaciones aplicables se ejecutaron correctamente.
- [ ] Los cambios fuera del alcance fueron descartados o autorizados.
- [ ] `memory-bank/progress.md` está actualizado cuando corresponde.

## Resultado esperado
Un informe breve con:
- Archivos revisados.
- Validaciones realizadas y sus resultados.
- Problemas encontrados.
- Conclusión: APTO o NO APTO para commit.

No realizar el commit automáticamente.
