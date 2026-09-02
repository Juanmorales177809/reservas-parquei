# app_flutter

Cliente Flutter multiplataforma (Móvil, Escritorio y Web) del sistema de gestión de reservas — reemplazo en curso de `frontend/` (Next.js). El backend (`backend/`, FastAPI) no cambia: este proyecto consume el mismo contrato REST.

Ver [`../CLAUDE.md`](../CLAUDE.md) (contexto general del monorepo) y [`CLAUDE.md`](CLAUDE.md) (detalle técnico de este proyecto: arquitectura de red/sesión, entornos, riesgos de dependencias conocidos).

## Estado

**Funcionalmente completo** — Flutter es la única UI del proyecto desde el cutover de la Fase 7 (`frontend/` Next.js retirado del repo). Última entrega **2026-09-02**: renombre completo `Espacio`→`Laboratorio`/`Zona`→`Espacio` en todo el código (Fases 1-7 de `~/.claude/plans/dazzling-wobbling-zebra.md`), catálogo real `tipos_reserva`/`motivos_solicitud` por laboratorio, propuesta/contrapropuesta de horarios sin pasar por `rechazada` (Fase C), forma única de reserva sin diálogo previo de motivo, links a la app en los correos salientes, y fix del bug de navbar al entrar al detalle de un laboratorio. Ver `CLAUDE.md` (detalle técnico completo, sección por fecha) y `../CHANGELOG.md` (registro cronológico factual) para el historial punto por punto.

## Requisitos

- Flutter SDK (canal `stable`) en el PATH.
- Para Windows desktop: Visual Studio con el workload "Desktop development with C++" (no incluido en esta instalación inicial).
- Para Android: Android Studio + Android SDK (no incluido en esta instalación inicial).
- Web: cualquier Chromium (Chrome/Edge) — funciona sin instalación adicional.

## Comandos

```bash
flutter pub get
flutter analyze
flutter test
flutter run -d chrome --dart-define-from-file=env/dev.json
flutter run -d windows --dart-define-from-file=env/dev.json
```

Tras modificar un modelo `@freezed`/`@JsonSerializable` o un provider `@riverpod`:

```bash
flutter pub run build_runner build
```

## Backend de desarrollo

El backend no expone su puerto al host en `docker-compose.yml` (solo lo alcanza `frontend` vía red interna de Docker). Para correr esta app contra un backend real en `localhost:8000` sin tocar `docker-compose.yml` ni la base de datos de desarrollo, ver la sección correspondiente en [`CLAUDE.md`](CLAUDE.md) (usa `reservas_test` + el backend corrido localmente con `uvicorn`, igual que ya documenta `../README.md` para desarrollo local del backend).
