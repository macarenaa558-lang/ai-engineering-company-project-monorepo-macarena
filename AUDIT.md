# Auditoría inicial de rendimiento frontend

## Alcance y metodología

Se analizaron las dos interfaces del monorepo con Lighthouse 13.4.1 en una ventana de incógnito, utilizando los perfiles Mobile y Desktop y las categorías Performance, Accessibility, Best Practices y SEO.

Las mediciones se realizaron sobre el servidor Vite de desarrollo ejecutado mediante Docker Compose. Por eso los valores de Performance pueden variar entre ejecuciones y reflejan recursos propios del modo desarrollo.

El website solo cuenta actualmente con una vista funcional, por lo que se auditó su página principal. En el backoffice se auditó el Gestor de Incidencias por ser una de las vistas más completas.

## Resultados iniciales

### Website — página principal

| Dispositivo | Performance | Accesibilidad | Buenas prácticas | SEO |
|---|---:|---:|---:|---:|
| Mobile | 52 | 91 | 100 | 75 |
| Desktop | 67 | 91 | 100 | 75 |

Métricas Mobile: FCP 11,3 s, LCP 20,8 s, TBT 220 ms y CLS 0.

Métricas Desktop: FCP 2,2 s, LCP 3,9 s, TBT 0 ms y CLS 0.

### Backoffice — Gestor de Incidencias

| Dispositivo | Performance | Accesibilidad | Buenas prácticas | SEO |
|---|---:|---:|---:|---:|
| Mobile | 43 | 70 | 96 | 82 |
| Desktop | 60 | 70 | 96 | 82 |

Métricas Mobile: FCP 15,6 s, LCP 29,0 s, TBT 490 ms y CLS 0.

Métricas Desktop: FCP 2,8 s, LCP 5,0 s, TBT 20 ms y CLS 0.

## Problemas detectados y causas raíz

### Website

- El documento no tenía una región principal `main`.
- El idioma del documento estaba configurado como inglés aunque la aplicación forma parte de un proyecto en español.
- Faltaban descripción meta, título descriptivo y un archivo `robots.txt` válido.
- Varias imágenes no declaraban dimensiones explícitas, lo que podía afectar la estabilidad visual.
- La imagen principal no tenía una prioridad de carga definida.
- El color de acento presentaba contraste insuficiente.
- Lighthouse detectó JavaScript sin minificar y carga elevada porque la auditoría se ejecutó sobre Vite en modo desarrollo.

### Backoffice

- El documento indicaba inglés como idioma principal.
- El título era genérico y no existía una descripción meta.
- No había un archivo `robots.txt` válido.
- La complejidad de la vista y el JavaScript del servidor de desarrollo aumentan FCP y LCP.
- Persisten oportunidades de accesibilidad dentro de formularios y controles complejos que requieren una revisión específica posterior.

## Candidatos a reutilización

1. Los formularios de Login, Register, ForgotPassword, ResetPassword y ChangePassword repiten estructura visual, mensajes y controles. Se podría extraer un componente reutilizable `AuthFormLayout`.
2. Las áreas de Incidencias, Proveedores e Inventario repiten encabezados, tarjetas, estados y acciones. Se podrían centralizar en componentes como `SectionHeader`, `StatusBadge` y `ActionButton`.
3. Las imágenes del website repetían atributos de carga, decodificación y dimensiones. Se extrajo `OptimizedImage` para centralizar esta lógica.

## Evidencias

Las capturas iniciales están disponibles en `audit/before/` y las posteriores en `audit/after/`.
