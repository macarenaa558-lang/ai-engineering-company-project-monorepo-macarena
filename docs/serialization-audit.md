# Auditoría de serialización del backend

## Objetivo

Esta auditoría revisa los endpoints de la API FastAPI de Brasaland para asegurar que cada operación tenga un contrato de respuesta explícito, estable y seguro.

Se verificaron los esquemas de entrada y salida, la exposición de campos sensibles y la documentación generada por OpenAPI.

## Criterios de clasificación

- ✅ **Ya serializado:** tenía un `response_model` explícito y adecuado.
- ⚠️ **Parcialmente serializado:** devolvía un diccionario filtrado o una respuesta controlada, pero no declaraba formalmente su esquema.
- ❌ **Sin serializar:** devolvía directamente un objeto interno, un ORM completo o un diccionario sin contrato definido.

## Estado inicial de los endpoints

| Método | Ruta                                  | Estado inicial | Observación                                                                         |
| ------ | ------------------------------------- | -------------: | ----------------------------------------------------------------------------------- |
| POST   | `/users`                              |             ⚠️ | Devolvía usuario y perfil filtrados, pero sin esquema explícito.                    |
| GET    | `/users`                              |             ⚠️ | Usaba `public_user`, pero sin `response_model`.                                     |
| GET    | `/users/{user_id}`                    |             ⚠️ | Filtraba la contraseña manualmente, sin contrato de salida.                         |
| PUT    | `/users/{user_id}`                    |             ⚠️ | Devolvía el usuario filtrado, sin esquema explícito.                                |
| DELETE | `/users/{user_id}`                    |             ⚠️ | Devolvía un mensaje sin esquema.                                                    |
| GET    | `/profiles/me`                        |             ⚠️ | Devolvía un diccionario de TinyDB sin esquema explícito.                            |
| PUT    | `/profiles/me`                        |             ⚠️ | Devolvía el perfil actualizado sin esquema explícito.                               |
| POST   | `/auth/login`                         |             ⚠️ | Devolvía el token en un diccionario sin contrato declarado.                         |
| GET    | `/auth/me`                            |             ⚠️ | Filtraba campos manualmente, pero no tenía `response_model`.                        |
| POST   | `/auth/forgot-password`               |             ⚠️ | Devolvía un mensaje sin esquema.                                                    |
| POST   | `/auth/reset-password`                |             ⚠️ | Devolvía un mensaje sin esquema.                                                    |
| POST   | `/auth/change-password`               |             ⚠️ | Devolvía un mensaje sin esquema.                                                    |
| POST   | `/suppliers`                          |             ✅ | Usaba `SupplierResponse`.                                                           |
| GET    | `/suppliers`                          |             ✅ | Usaba `list[SupplierResponse]`.                                                     |
| GET    | `/suppliers/{supplier_id}`            |             ✅ | Usaba `SupplierResponse`.                                                           |
| PATCH  | `/suppliers/{supplier_id}/rate`       |             ✅ | Usaba `SupplierResponse`.                                                           |
| PATCH  | `/suppliers/{supplier_id}/status`     |             ✅ | Usaba `SupplierResponse`.                                                           |
| DELETE | `/suppliers/{supplier_id}`            |             ⚠️ | Devolvía un mensaje sin esquema.                                                    |
| POST   | `/api/incidents`                      |             ✅ | Usaba `IncidentResponse`.                                                           |
| GET    | `/api/incidents`                      |             ✅ | Usaba `list[IncidentResponse]`.                                                     |
| GET    | `/api/incidents/summary`              |             ⚠️ | Devolvía métricas agregadas sin esquema.                                            |
| GET    | `/api/incidents/{incident_id}`        |             ✅ | Usaba `IncidentResponse`.                                                           |
| PATCH  | `/api/incidents/{incident_id}/status` |             ✅ | Usaba `IncidentResponse`.                                                           |
| GET    | `/inventory/products`                 |             ✅ | Usaba `list[IngredientResponse]`.                                                   |
| POST   | `/inventory/products`                 |             ✅ | Usaba `IngredientResponse`.                                                         |
| GET    | `/inventory/products/{product_id}`    |             ✅ | Usaba `IngredientResponse`.                                                         |
| POST   | `/inventory/orders/inbound`           |             ✅ | Usaba `IngredientEntryResponse`.                                                    |
| POST   | `/inventory/orders/outbound`          |             ✅ | Usaba `IngredientExitResponse`.                                                     |
| GET    | `/inventory/orders`                   |             ✅ | Usaba `list[OrderResponse]`.                                                        |
| POST   | `/api/incidents/analyze`              |             ⚠️ | Devolvía el análisis como diccionario sin esquema explícito.                        |
| GET    | `/api/incidents/results/export`       |             ⚠️ | Devolvía un CSV mediante `StreamingResponse`, pero no lo declaraba en el decorador. |

## Cambios implementados

Se creó `services/api/serialization_schemas.py` con los siguientes contratos reutilizables:

- `ProfileResponse`
- `UserResponse`
- `UserWithProfileResponse`
- `AuthMeResponse`
- `TokenResponse`
- `MessageResponse`
- `IncidentSummaryResponse`
- `IncidentAnalysisResponse`

También se añadió el módulo a la configuración de `setuptools` en `pyproject.toml`.

### Autenticación

Se agregaron esquemas de respuesta explícitos para:

- Inicio de sesión.
- Consulta del usuario autenticado.
- Solicitud de recuperación de contraseña.
- Restablecimiento de contraseña.
- Cambio de contraseña.

Las respuestas nunca incluyen `hashed_password`, contraseñas en texto plano, tokens internos de recuperación ni otros datos sensibles.

### Usuarios y perfiles

Se formalizaron los contratos de salida para usuarios y perfiles.

El esquema público del usuario expone únicamente:

- `id`
- `email`
- `is_active`
- `role`
- `created_at`

El campo `hashed_password` permanece exclusivamente en el servidor.

### Proveedores e incidentes

Los endpoints que ya tenían modelos se conservaron. Se añadieron esquemas explícitos para:

- Eliminación de proveedores.
- Resumen agregado de incidentes.
- Resultado del análisis de archivos CSV.

### Exportación CSV

El endpoint `/api/incidents/results/export` no utiliza un modelo JSON porque entrega un archivo. Su contrato se declara mediante:

```python
response_class=StreamingResponse
```
