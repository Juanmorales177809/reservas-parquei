# Prompt de traspaso — continuar Fase 6 en OpenCode

> Reemplaza la versión anterior de este archivo (que quedó obsoleta: describía
> la Fase 4b como "próximo paso", y ya se completaron las Fases 4b, 5 y buena
> parte de la 6). Copiá el bloque de abajo como primer mensaje.

---

## PROMPT PARA OPENCODE

Estás retomando la migración del frontend de **reservas-parquei** (sistema de reservas de espacios institucionales de una universidad: laboratorios, auditorios, salas) de Next.js a **Flutter**, en `D:\Repos\reservas-parquei\app_flutter\`. Otra sesión hizo todo el trabajo hasta ahora. La funcionalidad está **completa**; lo que queda es pulido de Fase 6.

### 1. Leé esto primero, en este orden

1. **`D:\Repos\reservas-parquei\app_flutter\CLAUDE.md`** — el más importante. Tiene el estado detallado, el sistema de diseño completo con los valores exactos, y una sección por cada bug real encontrado y cómo se corrigió. **No empieces a tocar nada sin leerlo entero.**
2. **`D:\Repos\reservas-parquei\CLAUDE.md`** (raíz) — reglas del proyecto.
3. `D:\Repos\reservas-parquei\app_flutter\HANDOFF_DISENO_FASE6.md` — el contexto de diseño que se le pasó a una IA experta; su respuesta es el checklist que estamos ejecutando.

### 2. Reglas duras (no negociables)

- **Nunca tocar `backend/`.** Ni schemas, ni routers, ni OpenAPI, ni la política de cookie/CORS. La app Flutter se adapta al contrato existente, nunca al revés. Si algo parece necesitar un cambio de backend, **paralo y preguntá** (ya pasó una vez: los "deltas" de los KPIs del dashboard requieren un dato que el backend no expone, y se documentó como pendiente en vez de tocarlo).
- **Nunca usar `reservas_db`** (la base de desarrollo de `docker-compose.yml`) ni producción. Solo `reservas_test` (puerto 5433, `docker-compose.test.yml`).
- **Nunca `git commit` ni `git push` sin autorización explícita del usuario en el mensaje actual.**
- **`app_flutter/` está entero SIN COMMITEAR** (untracked en git). Todo el trabajo vive solo en disco. No hagas `git clean`, `git reset --hard` ni nada que pueda borrarlo. Si vas a hacer cualquier operación destructiva, corré `git status` primero.
- Todo el código, la UI y la documentación van **en español**.

### 3. Estado actual

**Funcionalidad: Fases 0-5 COMPLETAS.** Auth (cookie HttpOnly), espacios públicos, reservas de usuario, notificaciones (polling 30s), gestión de reservas, CRUD de recursos/zonas/ensayos, editor de horario, usuarios (admin), dashboard con gráficos, auditoría. Todo verificado end-to-end contra el backend real.

**Fase 6 (pulido) EN CURSO.** El sistema de diseño se rehízo **tres veces**: el usuario rechazó Material 3 por defecto, después rechazó una paleta "arcoíris" de 6 gradientes, y finalmente dio una dirección concreta que sí lo convenció → **"tech-clean" académica**: azul profundo `#1E3A8A` + verde esmeralda `#10B981` acotado a estados positivos, esquinas muy redondeadas, sombras sutiles. **No propongas volver a un índigo/violeta genérico de SaaS ni a multicolor por tarjeta** — ya se descartaron explícitamente.

Sobre esa base se ejecutó una revisión de diseño externa. Lo hecho:
- Capa de color reescrita en `core/theme/app_colors.dart` con tokens verificados contra WCAG (corrigió dos fallos de contraste AA reales).
- Escala tipográfica de 9 niveles + `overline` + cifras tabulares (`app_typography.dart`).
- 5 niveles de elevación (`app_elevation.dart`), radios concéntricos, espaciado extendido.
- Tres *window size classes* (bottom nav / `RailNavShell` / top nav), ancho máximo de contenido 1280px.
- Dashboard reestructurado (hero + barra apilada 8/4, ejes enteros, heatmap con rampa discreta y leyenda).
- Slots de disponibilidad distinguidos **por patrón además de color** (WCAG 1.4.1) + selección por arrastre.
- Editor de horario con pintado por arrastre, toggle de fila/columna y **Deshacer**.
- Auditoría de tarjetas a filas densas con encabezado adhesivo por día.
- Estados vacíos geométricos y `ErrorView` diferenciado del vacío.
- `MediaQuery.disableAnimationsOf` respetado en las animaciones.

**Tests: 9** (eran 1). `flutter analyze` en "No issues found!".

### 4. Qué falta (en orden sugerido)

1. **Usuarios como tabla en escritorio** — la mitad pendiente del item 11 de la revisión. Auditoría ya se convirtió a filas; usuarios sigue en tarjetas. Con CRUD, una tabla con acciones a la derecha se recorre más rápido.
2. **Agrupar "Mis reservas" por tiempo** (Hoy / Esta semana / Próximas / Pasadas) con encabezados adhesivos, como ya se hizo en Auditoría por día. **Ojo**: no calcules "Hoy" comparando contra `DateTime.now()` sin pensarlo — ver punto 6.
3. **Una sola acción primaria por fila en gestión de reservas.** Hoy aprobar/rechazar/asistencia/cancelar están todas visibles y ninguna destaca; el resto debería ir en un menú `more-vertical`.
4. **Motivo obligatorio al rechazar una reserva** (diálogo con `TextField` requerido). Es un sistema institucional: un rechazo sin motivo genera un correo al gestor. **Verificá primero si el backend acepta un motivo** — si no lo acepta, esto NO se hace sin aprobación del usuario.
5. **Header comprimible** (`SliverAppBar` + `FlexibleSpaceBar`) en el detalle de espacio.
6. **Avatar con iniciales** en lugar del icono por rol en usuarios (el icono repite lo que ya dice el badge de rol).
7. **Fase 6 propiamente dicha**: compilar de verdad en Windows y Android. Hoy **solo se probó Web/Chrome** — faltan Visual Studio (workload C++) y Android SDK, que no están instalados. Nada garantiza que los targets nativos funcionen.
8. **Fase 6-Web**: proxy same-origin real como servicio de `docker-compose.yml`. **Requiere confirmación explícita del usuario** (toca Docker).

### 5. Cómo levantar el entorno de verificación

Nada de esto es automático ni persiste; hay que rearmarlo cada sesión.

```bash
# 1. Base de pruebas (desde la raíz del repo)
docker compose -f docker-compose.test.yml up -d --wait

# 2. Backend LOCAL (no Docker) contra reservas_test, desde backend/
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/reservas_test"
export SECRET_KEY="dev-secret-key-for-local-flutter-verification-only"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
export APP_TIMEZONE="America/Bogota"
export ENVIRONMENT="development"
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. Build + proxy same-origin desechable (necesario para que la cookie
#    HttpOnly sea same-origin en el navegador)
cd app_flutter
flutter build web --dart-define-from-file=env/web.json
python <scratchpad>/dev_same_origin_proxy.py   # sirve build/web y proxea /api/* → :8000
```

El script del proxy está documentado en `CLAUDE.md` (sección "Cómo se verificó la Fase 0"). Abrí `http://127.0.0.1:8090`. **No hay hot reload con este método**: hay que repetir `flutter build web` en cada cambio (~100s).

Usuarios de prueba ya creados en `reservas_test`:
- `admin_flutter` / `ClaveFase0Temp123` (admin)
- `gestor_flutter` / `ClaveGestor123` (gestor, espacio "Auditorio Principal", id 1)

Atajo útil para cambiar de sesión sin pelear con el formulario:
```js
fetch('/api/auth/logout',{method:'POST',credentials:'same-origin'})
  .then(()=>fetch('/api/auth/login',{method:'POST',credentials:'same-origin',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:'admin_flutter',password:'ClaveFase0Temp123'})}))
```

### 6. Trampas conocidas (te van a morder si no las sabés)

- **Errores de API**: `dio` siempre lanza `DioException`, nunca `ApiException`. Usá **siempre** los helpers `apiErrorMessage(e, fallback: ...)` / `apiErrorStatusCode(e)` de `core/network/api_exception.dart`. Nunca `e is ApiException` sobre el error crudo.
- **Fechas y horas**: el backend devuelve `datetime` **naive** en `America/Bogota`. **Nunca `DateTime.parse`.** Se manejan como texto crudo con helpers de formato manual. Por eso Auditoría no dice "Hoy"/"Ayer": compararlo contra la fecha local del dispositivo daría una etiqueta equivocada fuera de esa zona, y es un error silencioso.
- **`AsyncValue.valueOrNull` no existe** en esta versión de Riverpod — usá `.value`.
- **`freezed` está en dev-prerelease `4.0.0-dev.3`** — es la única versión compatible con `riverpod_generator`. No la "arregles" a una estable sin volver a resolver el conflicto de `analyzer`.
- **`phosphor_flutter` no compila** en este SDK (`IconData` es `final class`). Usamos `lucide_icons_flutter`. El error **solo aparece al compilar de verdad**, no en `flutter analyze`.
- **`GestureDetector` con drag: usá `dragStartBehavior: DragStartBehavior.down`.** Con el default (`.start`), Flutter reporta el inicio del arrastre *después* del umbral táctil (~18px) y el ancla cae en el elemento equivocado. Ya mordió una vez.
- **`CrossAxisAlignment.stretch` en un `Row` dentro de un scroll de altura no acotada** hace colapsar toda la fila (el dashboard se renderizó **vacío** por esto, con la API respondiendo 200).
- **Un `TextButton` con `onPressed: null` está deshabilitado**, y Material ignora tu `foregroundColor`. Por esto el destino activo del top nav se veía apagado.
- **Animaciones en bucle infinito (`.repeat()`) rompen los widget tests** bajo `FakeAsync` ("Pending timers"). Además la revisión de diseño las desaconseja como adorno.
- **`flutter analyze` y `flutter test` en verde NO garantizan que la app funcione.** Varios de los bugs de arriba pasaron análisis limpio y solo aparecieron probando contra el backend real. **Verificá siempre el flujo real antes de dar algo por terminado.**

### 7. Comandos

```bash
cd app_flutter
flutter pub run build_runner build   # tras tocar modelos @freezed o providers @riverpod
flutter analyze                       # debe quedar "No issues found!"
flutter test                          # 9 tests, todos deben pasar
```

### 8. Cómo trabajar

Seguí el patrón ya establecido: leé el schema Pydantic del backend **antes** de escribir un modelo (no asumas), modelo `@freezed` → repositorio → provider `@riverpod` → pantalla. Usá los tokens de `core/theme/` (`AppColors`, `AppEstados`, `AppText`, `AppSpacing`, `AppRadius`, `AppElevation`), nunca `Color(0xFF...)` sueltos ni `SizedBox(height: 8)` con números mágicos.

Preguntale al usuario con cuál de los puntos de la sección 4 querés que empieces, o si prefiere revisar el estado actual primero.
