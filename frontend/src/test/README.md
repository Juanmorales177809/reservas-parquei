# test

## Propósito

Infraestructura de pruebas del frontend: setup global de Vitest + Testing Library.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| setupTests.ts | Creado | Registra los matchers de `@testing-library/jest-dom` para Vitest, limpia el DOM con `cleanup()` y aísla `localStorage` después de cada test |

## Reglas de negocio relacionadas

- Infraestructura de calidad (sin reglas de negocio directas).

## Decisiones técnicas

- `globals` de Vitest desactivados: los tests importan `describe/it/expect/vi` explícitamente, evitando tocar el `tsconfig.json`.
- Los mocks de módulos (`next/navigation`, servicios, AuthContext) se declaran por archivo de test con `vi.hoisted`; se restauran automáticamente (`restoreMocks: true` en `vitest.config.ts`).
- No se incluyen tokens reales ni datos de producción: solo cadenas de prueba (`token-de-prueba`, emails `@test.com`).

## Pruebas

```powershell
npm run test          # una sola pasada
npm run test:watch    # modo watch
npm run test:coverage # cobertura informativa (v8)
```

## Impacto y compatibilidad

- Sin impacto en producción (archivo solo de test, no importado por la app).

## Pendientes

- E2E con Playwright (fuera de esta fase; infraestructura futura).

## Fase de implementación

Fase 5B.
