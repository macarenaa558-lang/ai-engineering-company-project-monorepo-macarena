# Brasaland — Informe de optimización de rendimiento

## 1. Objetivo

Optimizar el rendimiento del backoffice de análisis de incidentes de Brasaland mediante Lazy Loading, memoización en React y caché con TTL en FastAPI.

## 2. Optimización del frontend

### Lazy Loading

Se separaron dos componentes del archivo principal `App.tsx`:

- `CategoryPanel.tsx`: presenta la distribución de incidentes por categoría.
- `StatusPanel.tsx`: presenta la distribución de incidentes por estado.

Ambos componentes se cargan mediante `React.lazy` y `Suspense`.

**Justificación:** estos paneles solamente se muestran después de analizar un archivo CSV. No es necesario incluir su código en la carga inicial de la aplicación.

### Memoización con useMemo

Se implementó `useMemo` en ambos componentes para transformar los conteos de incidentes en estructuras que incluyen sus porcentajes.

Dependencias utilizadas:

- `analysis.category_counts` y `analysis.valid_records`.
- `analysis.status_counts` y `analysis.valid_records`.

Esto evita repetir las transformaciones cuando los datos del análisis no cambian.

**Limitación:** actualmente existen pocas categorías y estados, por lo que la mejora de rendimiento de `useMemo` puede ser pequeña. Su utilidad aumentaría si las agrupaciones fueran más numerosas o complejas.

## 3. Análisis de endpoints del backend

| Endpoint                              | Costo de procesamiento                                                | Frecuencia esperada               | Cambios en los datos                    | Decisión             |
| ------------------------------------- | --------------------------------------------------------------------- | --------------------------------- | --------------------------------------- | -------------------- |
| POST /api/incidents/analyze           | Alto en archivos grandes: lectura, validación y análisis de registros | Al cargar informes                | Cada carga puede cambiar los resultados | Sin caché            |
| GET /api/incidents/results/export     | Medio: genera un archivo CSV con las métricas                         | Cuando se descarga un informe     | Cambia después de un análisis           | Sin caché            |
| GET /api/incidents/results/summary    | Bajo: selecciona métricas del último análisis                         | Consultas repetidas del resumen   | Cambia después de un análisis           | Caché de 60 segundos |
| GET /api/incidents/results/categories | Bajo: calcula porcentajes por categoría                               | Consultas repetidas de categorías | Cambia después de un análisis           | Caché de 60 segundos |

Los dos últimos endpoints se incorporaron para ofrecer consultas de lectura reutilizables.

## 4. Estrategia de caché

Se implementó un caché en memoria mediante un diccionario de Python.

Características:

- TTL de 60 segundos.
- Uso de `time.monotonic()` para controlar el vencimiento.
- Protección con `threading.Lock`.
- Copias independientes mediante `deepcopy`.
- Invalidación completa cuando se procesa correctamente un nuevo CSV.

### Justificación del TTL

Se seleccionó un TTL de 60 segundos para limitar el tiempo de conservación de los resultados en memoria.

La invalidación inmediata después de cada análisis permite que las consultas posteriores obtengan los datos actualizados sin esperar al vencimiento.

### Datos que no se cachean

No se cachea `POST /api/incidents/analyze` porque recibe archivos que pueden contener información diferente y debe procesar cada nueva carga.

Tampoco se cachea la exportación CSV, para mantener sencilla la generación del archivo correspondiente al análisis más reciente.

## 5. Pruebas realizadas

### Frontend

Se ejecutó `npm run build` exitosamente.

Vite generó archivos independientes para:

- `CategoryPanel`.
- `StatusPanel`.

Esto confirma la separación del código en módulos de carga diferida.

### Backend

Se realizaron pruebas para verificar:

- Almacenamiento y recuperación de datos en caché.
- Independencia de los objetos recuperados.
- Invalidación manual del caché.
- Vencimiento del TTL mediante simulación del tiempo.
- Respuestas HTTP de los endpoints de resumen y categorías.
- Actualización de resultados después de invalidar el caché.

Las pruebas mencionadas finalizaron correctamente.

## 6. Comparación de rendimiento

Antes de las optimizaciones, el frontend compilaba en un único archivo JavaScript principal de aproximadamente 197,79 kB sin comprimir.

Después de implementar Lazy Loading, Vite generó módulos independientes para los dos paneles.

No se realizaron todavía mediciones controladas de latencia HTTP antes y después del caché. Por lo tanto, no se afirma una reducción porcentual de los tiempos de respuesta.

## 7. Limitaciones y mejoras futuras

- El caché es local al proceso de Python y no se comparte entre múltiples trabajadores o servidores.
- Los resultados del análisis también se almacenan en memoria, por lo que se pierden al reiniciar el servidor.
- En la rama de integración, los endpoints de resultados exigen autenticación y los resultados y la caché se separan por usuario y versión de análisis (ver `services/README.md`). Los resultados siguen siendo temporales y por proceso.
- Para una aplicación distribuida podría utilizarse Redis.
- Se recomienda medir latencia, tasa de aciertos del caché y comportamiento con archivos grandes.
- También se recomienda realizar pruebas de integración con cargas reales de CSV y comprobar la experiencia visual del frontend.

## 8. Conclusión

Se implementaron técnicas de optimización tanto en React como en FastAPI, priorizando la carga diferida de componentes, la reutilización de cálculos y el almacenamiento temporal de consultas de lectura.

Las mejoras proporcionan una base para continuar optimizando el rendimiento del backoffice de Brasaland.
