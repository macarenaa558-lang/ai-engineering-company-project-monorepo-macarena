# Plan de pruebas - API de autenticación

## Objetivo

Este documento describe el plan de pruebas unitarias para la API de autenticación de Brasaland.

La suite está enfocada en validar la lógica de negocio de autenticación y recuperación de contraseña, evitando probar detalles internos del framework FastAPI.

## Cómo ejecutar las pruebas

Desde la carpeta `services/api`:

```bash
uv run pytest
```

Para ejecutar las pruebas con cobertura:

```bash
uv run pytest --cov=auth --cov-report=term-missing
```

El objetivo mínimo es alcanzar un 70% de cobertura en el módulo de autenticación.

## Endpoints cubiertos

### POST /auth/login

Casos planificados:

- Camino feliz: usuario existente con contraseña correcta obtiene un access token.
- Caso límite: usuario inexistente intenta iniciar sesión.
- Fallo: usuario existente ingresa una contraseña incorrecta.

### GET /auth/me

Casos planificados:

- Camino feliz: usuario autenticado obtiene sus datos y perfil.
- Caso límite: usuario autenticado sin perfil obtiene sus datos correctamente.
- Fallo: token inválido o expirado no permite acceder al usuario actual.

### POST /auth/forgot-password

Casos planificados:

- Camino feliz: email registrado genera un token de recuperación y se intenta enviar el correo.
- Caso límite: email no registrado devuelve una respuesta genérica para evitar revelar si la cuenta existe.
- Fallo: error del servicio de correo invalida los tokens creados y devuelve un error controlado.

### POST /auth/reset-password

Casos planificados:

- Camino feliz: token válido permite cambiar la contraseña y queda marcado como utilizado.
- Caso límite: token ya utilizado no puede volver a usarse.
- Fallo: token inexistente o expirado no permite cambiar la contraseña.

### POST /auth/change-password

Casos planificados:

- Camino feliz: contraseña actual correcta permite establecer una nueva contraseña.
- Caso límite: al cambiar la contraseña se invalidan los tokens de recuperación previos.
- Fallo: contraseña actual incorrecta impide el cambio.

## Casos identificados con asistencia de IA

Durante la revisión del código se identificaron casos que pueden pasarse por alto fácilmente:

- Un token de recuperación ya utilizado no debe poder reutilizarse.
- Los tokens de recuperación anteriores deben invalidarse al cambiar la contraseña.
- Un fallo en el proveedor de correo debe invalidar el token recién generado.
- La respuesta de recuperación de contraseña debe ser genérica aunque el email no exista, para evitar enumeración de usuarios.

Estos casos se incluirán en la suite de pruebas.

## Resultados

La suite de autenticación se ejecutó correctamente: 16 pruebas aprobadas y 0 fallidas. La cobertura obtenida para el módulo auth.py fue del 94%, superando el mínimo requerido del 70%.

## Pruebas de autenticación en TypeScript

Las utilidades de autenticación del backoffice ubicadas en `uis/backoffice/src/services/auth.ts` se probaron con Jest y ts-jest.

Casos cubiertos:

- Guardado y recuperación del token.
- Ausencia de token.
- Eliminación del token.
- Estado autenticado y no autenticado.
- Inclusión del encabezado `Authorization` cuando existe un token.
- Ausencia del encabezado `Authorization` cuando no existe un token.
- Eliminación del token ante una respuesta HTTP 401.

Para ejecutar las pruebas:

```bash
cd uis/backoffice
npm test
```

Para ejecutar las pruebas con cobertura:

```bash
cd uis/backoffice
npm test -- --coverage
```

Resultado obtenido: 8 pruebas aprobadas y 0 fallidas. La cobertura de `auth.ts` fue de 96.15% en statements, 85.71% en branches, 100% en functions y 95.23% en lines.
