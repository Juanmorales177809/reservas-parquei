# Pruebas de extremo a extremo (Playwright)

Contra la aplicación real, con el navegador del sistema (`msedge`; `E2E_CHANNEL=chrome` para otro).

```bash
npm run build && npm start      # frontend en http://localhost:3000; reenvía /api al backend (BACKEND_URL)
npm run e2e                     # todas las pruebas
```

## Qué necesitan

Una base **copia** de la viva (nunca la viva: las pruebas crean cuentas, reservas y adjuntos):

```bash
docker exec reservas_db psql -U postgres -c "CREATE DATABASE reservas_e2e TEMPLATE reservas_db"
POSTGRES_DB=reservas_e2e docker compose up -d --build backend
```

y estos datos sembrados en ella (ver `e2e/cuentas.ts` para las cuentas):

- una cuenta de personal con todos los permisos globales y una cuenta `USUARIO`;
- el laboratorio **«Laboratorio de Redes»** con su configuración (lunes a viernes 07:00–19:00, sin antelación),
  los tipos Espacio, Recurso interno y Lista de espera habilitados, y el cargo del personal en esa unidad;
- el espacio **«Sala de Redes»** (capacidad 20) con un campo obligatorio de texto **«Ensayo previsto»** y
  dos recursos asociados; los mobiliarios **«Silla E2E»**, **«Mesa de soldadura»** y **«Lupa de banco»**;
- el proyecto **«Proyecto E2E» (E2E-1)**.

## Límite de inicios de sesión

El backend permite 5 intentos de login por cuenta cada 15 minutos (`SEC-ABU-02`). Una corrida completa
usa 3 de la cuenta de administrador. Si repites la suite enseguida y el login falla con «temporalmente
limitada», reinicia el backend de pruebas (`docker restart reservas_backend`), que guarda el contador en memoria.
