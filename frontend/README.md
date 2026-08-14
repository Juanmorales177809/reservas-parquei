# frontend

## Propósito

Aplicación Next.js 14 (App Router) del sistema de reservas. Consume la API del backend exclusivamente mediante rutas relativas `/api` (rewrites de `next.config.js`).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| .eslintrc.json | Creado | Configuración ESLint explícita (`next/core-web-vitals`) para Next.js 14 con el ESLint 8 ya declarado en `package.json`; sin dependencias nuevas ni cambios de lockfile |
| vitest.config.ts | Creado | Configuración de Vitest: entorno jsdom, plugin React, alias `@/*`, setup global y cobertura informativa v8 (Fase 5B) |
| package.json | Modificado | Scripts `test`, `test:watch` y `test:coverage` + dev-deps de pruebas aprobadas (Vitest 2.1, RTL 16, jest-dom 6, user-event 14, jsdom 25, plugin-react 4, coverage-v8) (Fase 5B) |

## Reglas de negocio relacionadas

- Infraestructura de calidad: habilita `npm run lint` (antes fallaba pidiendo configurar ESLint).

## Decisiones técnicas

- Se usó la configuración clásica (`.eslintrc.json`) por ser la compatible con Next 14 + ESLint 8 (flat config no está soportado en Next 14).

## Pruebas

```powershell
npm run test          # Vitest (unitarias y de componentes)
npm run test:watch    # modo watch
npm run test:coverage # cobertura informativa
npm run lint          # ESLint (next/core-web-vitals)
npm run type-check    # tsc --noEmit
```

Detalle de la infraestructura, mocks y límites en `src/test/README.md`.

## Impacto y compatibilidad

- Sin impacto funcional; solo habilita el comando de lint existente.

## Pendientes

- N/A.

## Fase de implementación

Fase 5A.
