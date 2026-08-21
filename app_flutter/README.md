# app_flutter

Cliente Flutter multiplataforma (Móvil, Escritorio y Web) del sistema de gestión de reservas — reemplazo en curso de `frontend/` (Next.js). El backend (`backend/`, FastAPI) no cambia: este proyecto consume el mismo contrato REST.

Ver [`../CLAUDE.md`](../CLAUDE.md) (contexto general del monorepo) y [`CLAUDE.md`](CLAUDE.md) (detalle técnico de este proyecto: arquitectura de red/sesión, entornos, riesgos de dependencias conocidos).

## Estado

**Fases 0-4 completas + Fase 5 parcial (usuarios)** (ver `CLAUDE.md` para detalle). Última entrega **Fase 5 Usuarios (2026-08-20)**: `GestionUsuariosScreen` (`/usuarios`, solo admin) — listar/crear/editar/eliminar (`POST 201 409 username/email, 400 gestor sin espacio; PUT 200 409 self/last-admin con `pg_advisory_xact_lock`; DELETE 204 409`, validación `username 3..80, email @., password 6..72`), guard `admin-only` (`403` gestor → `/espacios`), `Tú` chip + sin botón Eliminar propio. Previa **Fase 4b**: CRUD recursos/zonas/ensayos + editor `horario_atencion` 6-22. Todo verificado en vivo con Playwright contra `reservas_test:5433` (gestor `gestor_flutter`, admin `admin_flutter`), `flutter analyze` No issues, `flutter test` 1/1.

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
