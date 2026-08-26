# Prompt de traspaso — correo saliente (reservas, alta de usuario, recuperación)

> Reemplaza la versión anterior de este archivo (Fase 6 de diseño, ya completada
> hace tiempo y sin relación con el trabajo actual). Copiá el bloque de abajo
> como primer mensaje en OpenCode.

---

## PROMPT PARA OPENCODE

Estás retomando **reservas-parquei** (sistema de reservas de espacios de una universidad) en `C:\Users\santi\Desktop\Repos\reservas-parquei`. Otra sesión (Claude Code) acaba de implementar y verificar una feature completa de **correo saliente** — está terminada en código y tests, pero **sin commitear**. Tu trabajo es revisarla, verificarla si podés contra un backend real, y decidir con el usuario si se commitea.

### 1. Leé esto primero, en este orden

1. **`CLAUDE.md`** (raíz) — reglas del proyecto. Ya incluye la sección "Despliegue continuo (CD)" describiendo el agente pull que corre en el bastión.
2. **`backend/CLAUDE.md`**, **`backend/tests/CLAUDE.md`**, **`app_flutter/CLAUDE.md`** (este último tiene, al principio, la sección `## Correo saliente: alta de usuario y recuperación de contraseña (2026-08-26)` con el resumen exacto de lo que cambió del lado Flutter).
3. **`C:\Users\santi\.claude\plans\ya-tenemos-el-ci-calm-octopus.md`** — el documento de diseño completo de esta feature, con el veredicto (no migrar a Supabase Auth) y el diseño de los tres flujos aprobado por el usuario.
4. Memoria de sesión sobre el ticket de IT pendiente: `C:\Users\santi\.claude\projects\C--Users-santi-Desktop-Repos-reservas-parquei\memory\smtp_itm_tenant_auth.md`.

### 2. Reglas duras (no negociables)

- **No `git commit` ni `git push` sin autorización explícita del usuario en el mensaje actual.** Todo lo de esta feature está en el árbol de trabajo, sin commitear, a propósito — no lo commitees por tu cuenta aunque "esté listo".
- **No usar `reservas_db`** (desarrollo) ni ninguna base de producción. Solo `reservas_test` (puerto 5433, `docker-compose.test.yml`).
- **No modificar contratos de API/OpenAPI sin aprobación explícita separada.** Esta feature YA tiene una excepción aprobada y aplicada (3 endpoints nuevos + `debe_cambiar_password`, ver `backend/tests/openapi.snapshot.json` ya regenerado) — cualquier cambio ADICIONAL de contrato necesita su propia aprobación, esta no la cubre.
- Antes de cualquier operación destructiva (`git reset --hard`, `git clean`, etc.), corré `git status` primero — hay 42 archivos modificados/nuevos sin commitear.
- Todo el código, la UI y la documentación van **en español**.

### 3. Qué se hizo y cómo se verificó

Tres flujos, backend y Flutter completos:

| Flujo | Qué hace |
|---|---|
| Reservas | Notifica por correo a gestores (pendiente) y al dueño (aprobada/rechazada/cancelada), junto a la `Notificacion` in-app que ya existía |
| Alta de usuario | El backend genera la contraseña (ignora la que mande el cliente), la entrega por correo, marca `debe_cambiar_password` |
| Recuperación | Código de 6 dígitos por correo, en memoria del proceso (nunca en la base), rate-limited |

**Backend**: `cd backend && .venv/Scripts/python.exe -m pytest -q` (requiere `reservas_test` arriba, `docker compose -f docker-compose.test.yml up -d --wait` desde la raíz) → **645/645 passed** en la última corrida.

**Flutter**: sin SDK local instalado en esta máquina — se verifica con el contenedor descartable documentado en `app_flutter/CLAUDE.md` (sección "Buildear la Web en un host SIN Flutter instalado"), corriendo `flutter analyze` y `flutter test` en vez de build web. Última corrida: **`No issues found!`** y **29/29 passed**.

Decisiones de implementación que se desviaron del diseño original por lo que se encontró leyendo el código real (documentadas, no arbitrarias):
- **`smtplib` de la stdlib, no `aiosmtplib`**: todo el backend es síncrono, meter una librería async solo para esto habría sido el único punto async del proyecto.
- **Sin worker en segundo plano**: el envío se intenta sincrónicamente justo después de confirmar la operación de negocio (que ya se guardó antes de intentar el correo), con `try/except` amplio. Se reintenta también una vez en el `lifespan` (autocuración tras reinicio).
- **El código de recuperación vive en un diccionario en memoria** (`app/services/recuperacion.py`), no en una tabla ni en Redis — mismo patrón y misma limitación aceptada que el limitador de login existente.

### 4. Archivos tocados (git status al momento de este handoff)

```
 M .env.example
 M app_flutter/CLAUDE.md
 M app_flutter/lib/core/network/auth_interceptor.dart
 M app_flutter/lib/core/router/app_router.dart
 M app_flutter/lib/core/router/app_routes.dart
 M app_flutter/lib/features/auth/application/auth_provider.dart
 M app_flutter/lib/features/auth/application/auth_provider.g.dart
 M app_flutter/lib/features/auth/data/auth_repository.dart
 M app_flutter/lib/features/auth/domain/auth_user.dart
 M app_flutter/lib/features/auth/domain/auth_user.freezed.dart
 M app_flutter/lib/features/auth/domain/auth_user.g.dart
 M app_flutter/lib/features/auth/presentation/login_screen.dart
 M app_flutter/lib/features/usuarios/data/usuarios_repository.dart
 M app_flutter/lib/features/usuarios/presentation/gestion_usuarios_screen.dart
 M app_flutter/lib/features/zonas/application/zonas_providers.g.dart   ← staleness de una sesión anterior, no de esta feature
 M backend/app/api/README.md
 M backend/app/api/auth.py
 M backend/app/api/usuarios.py
 M backend/app/config.py
 M backend/app/crud/usuarios.py
 M backend/app/main.py
 M backend/app/migrations.py
 M backend/app/models/README.md
 M backend/app/models/__init__.py
 M backend/app/models/usuario.py
 M backend/app/schemas/README.md
 M backend/app/schemas/usuario.py
 M backend/app/services/README.md
 M backend/app/services/rate_limit.py
 M backend/app/services/reservas.py
 M backend/tests/openapi.snapshot.json
 M backend/tests/test_schemas_contrato.py
 M docker-compose.yml
?? app_flutter/lib/features/auth/presentation/cambiar_password_temporal_screen.dart
?? app_flutter/lib/features/auth/presentation/recuperar_password_screen.dart
?? app_flutter/lib/features/auth/presentation/restablecer_password_screen.dart
?? app_flutter/test/features/auth/presentation/password_flows_test.dart
?? backend/app/models/correo_saliente.py
?? backend/app/services/email.py
?? backend/app/services/recuperacion.py
?? backend/tests/test_api_password.py
?? backend/tests/test_correo_saliente.py
```

Si `git status` no coincide con esto, alguien más tocó el repo desde este handoff — investigá el diff antes de asumir nada.

### 5. Qué falta (honesto, no inventado)

1. **Verificación manual contra un backend real.** Todo esto pasó tests automatizados y análisis estático, pero eso no garantiza que el flujo se sienta bien en uso real — ya pasó varias veces en este proyecto que algo pasa análisis y tests y falla en la práctica. Nadie levantó la app y probó los tres flujos a mano todavía.
2. **Mailpit no está levantado.** Para probar el envío real en desarrollo: `docker compose --profile dev up -d mailpit` + `EMAIL_ENABLED=true`/`SMTP_HOST=mailpit`/`SMTP_PORT=1025`/`SMTP_STARTTLS=false` en el `.env`. Ver `http://localhost:8025` para lo que se mandó.
3. **El ticket a IT del ITM sigue pendiente** (excepción de SMTP AUTH para el buzón de servicio, tenant tiene SMTP AUTH desactivado por defecto — confirmado por prueba real, ver el archivo de memoria de la sección 1). Con `EMAIL_ENABLED=false` (default) todo esto se puede desplegar sin enviar nada real, así que esto no bloquea nada.
4. **Decidir con el usuario si se commitea.** Nada de esto se pusheó; el agente de CD del bastión (ver `CLAUDE.md` raíz) solo despliega lo que llega a `feature/soV0.1` en verde.

### 6. Comandos

```bash
# Backend
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz
cd backend && .venv/Scripts/python.exe -m pytest -q

# Flutter (sin SDK local — ver app_flutter/CLAUDE.md, sección del contenedor descartable)
# dentro del contenedor, desde app_flutter/:
flutter analyze
flutter test
```

### 7. Cómo trabajar

No reabras el diseño desde cero: el plan ya fue discutido, cuestionado (se evaluó y descartó migrar a Supabase Auth, con evidencia concreta) y aprobado. Si encontrás un bug real al verificar manualmente, arreglalo y agregá el test que lo cubra (regla del proyecto: todo cambio de comportamiento necesita su test, ver `backend/tests/CLAUDE.md`). Si algo requiere tocar un contrato de API que no está ya en la lista de la sección 3, parate y preguntale al usuario antes de tocarlo.
