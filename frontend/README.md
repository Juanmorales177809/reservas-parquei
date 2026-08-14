# frontend

## Propósito

Aplicación Next.js 14 (App Router) del sistema de reservas. Consume la API del backend exclusivamente mediante rutas relativas `/api` (rewrites de `next.config.js`).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| .eslintrc.json | Creado | Configuración ESLint explícita (`next/core-web-vitals`) para Next.js 14 con el ESLint 8 ya declarado en `package.json`; sin dependencias nuevas ni cambios de lockfile |

## Reglas de negocio relacionadas

- Infraestructura de calidad: habilita `npm run lint` (antes fallaba pidiendo configurar ESLint).

## Decisiones técnicas

- Se usó la configuración clásica (`.eslintrc.json`) por ser la compatible con Next 14 + ESLint 8 (flat config no está soportado en Next 14).

## Pruebas

- `npm run lint` → 0 warnings/errores.

## Impacto y compatibilidad

- Sin impacto funcional; solo habilita el comando de lint existente.

## Pendientes

- N/A.

## Fase de implementación

Fase 5A.
