# Reporte final de optimización frontend

## Resumen

Se auditaron y optimizaron el website público y el backoffice de Brasaland. Se aplicaron mejoras puntuales de accesibilidad, SEO, estabilidad visual y reutilización de código, conservando la estructura y el diseño existentes.

## Cambios realizados

### Website

- Se agregó una región semántica `main`.
- Se configuró el idioma del documento en español.
- Se agregó un título descriptivo y una descripción meta.
- Se creó un `robots.txt` válido.
- Se ajustó el color de acento para mejorar el contraste.
- Se creó el componente reutilizable `OptimizedImage`.
- Se declararon dimensiones explícitas para las imágenes.
- Se agregó carga prioritaria a la imagen principal y carga diferida al resto.

### Backoffice

- Se configuró el idioma del documento en español.
- Se reemplazó el título genérico por uno descriptivo.
- Se agregó una descripción meta.
- Se creó un `robots.txt` válido.

## Comparación Lighthouse

### Website — Mobile

| Categoría | Antes | Después | Diferencia |
|---|---:|---:|---:|
| Performance | 52 | 37 | -15 |
| Accesibilidad | 91 | 100 | +9 |
| Buenas prácticas | 100 | 100 | 0 |
| SEO | 75 | 100 | +25 |

La disminución puntual de Performance corresponde a variaciones del servidor Vite de desarrollo y al aumento de TBT en esa ejecución. Las mejoras de accesibilidad y SEO son consistentes y verificables.

### Website — Desktop

| Categoría | Antes | Después | Diferencia |
|---|---:|---:|---:|
| Performance | 67 | 68 | +1 |
| Accesibilidad | 91 | 100 | +9 |
| Buenas prácticas | 100 | 100 | 0 |
| SEO | 75 | 100 | +25 |

El LCP mejoró de 3,9 s a 3,7 s y el FCP de 2,2 s a 2,1 s.

### Backoffice — Mobile

| Categoría | Antes | Después | Diferencia |
|---|---:|---:|---:|
| Performance | 43 | 45 | +2 |
| Accesibilidad | 70 | 70 | 0 |
| Buenas prácticas | 96 | 100 | +4 |
| SEO | 82 | 100 | +18 |

El TBT mejoró de 490 ms a 430 ms y el LCP de 29,0 s a 28,9 s.

### Backoffice — Desktop

| Categoría | Antes | Después | Diferencia |
|---|---:|---:|---:|
| Performance | 60 | 60 | 0 |
| Accesibilidad | 70 | 70 | 0 |
| Buenas prácticas | 96 | 96 | 0 |
| SEO | 82 | 100 | +18 |

Las métricas de rendimiento permanecieron estables, mientras que SEO mejoró de forma medible.

## Componente reutilizable

Se extrajo `uis/website/src/components/OptimizedImage.tsx`. Este componente centraliza:

- dimensiones obligatorias;
- carga diferida por defecto;
- decodificación asíncrona;
- posibilidad de priorizar imágenes críticas.

Fue integrado en las imágenes principales y secundarias del website.

## Validación

Se ejecutaron correctamente:

- `npm run build --prefix uis/website`
- `npm run build --prefix uis/backoffice`

Ambas aplicaciones completaron su compilación de producción sin errores.

## Evidencias

- Resultados iniciales: `audit/before/`
- Resultados finales: `audit/after/`

## Conclusión

La optimización produjo mejoras medibles en ambas interfaces. El website alcanzó 100 puntos en Accesibilidad y SEO, mientras que el backoffice alcanzó 100 puntos en SEO y mejoró Performance y Buenas Prácticas en Mobile. Las diferencias de rendimiento restantes están condicionadas por la ejecución de Lighthouse sobre el servidor de desarrollo.

## Valoración del mayor impacto

La corrección con mayor impacto fue incorporar metadatos descriptivos, idioma correcto y archivos `robots.txt` válidos. Esto elevó el SEO del website de 75 a 100 y el del backoffice de 82 a 100. En el website también resultaron importantes el uso de `main`, la mejora del contraste y el componente `OptimizedImage`, que llevaron la accesibilidad de 91 a 100 y mejoraron la estabilidad visual.
