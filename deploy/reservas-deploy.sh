#!/usr/bin/env bash
#
# Agente de despliegue continuo (modelo *pull*) para el servidor.
#
# Por qué pull y no push: el servidor tiene IP privada, así que los runners
# de GitHub no pueden alcanzarlo; y quien opera esto no es admin del repo,
# así que no puede registrar un runner self-hosted ni crear secrets. Este
# agente invierte la dirección: el servidor consulta GitHub, GitHub nunca
# entra. Solo necesita salida a internet y un token de lectura.
#
# Qué hace, en una línea: si la última corrida VERDE de CI en la rama tiene
# un commit distinto al desplegado, baja el bundle web que publicó esa
# corrida, deja el checkout en ese commit exacto, y converge el stack.
#
# Uso: reservas-deploy [--force]
#   --force  despliega aunque el SHA ya figure como desplegado.
#
set -Eeuo pipefail

# --- Configuración (sobrescribible por entorno / EnvironmentFile) ---------
OWNER="${OWNER:-Juanmorales177809}"
REPO="${REPO:-reservas-parquei}"
BRANCH="${BRANCH:-feature/soV0.1}"
WORKFLOW="${WORKFLOW:-ci.yml}"
ARTIFACT="${ARTIFACT:-flutter-web}"
REPO_DIR="${REPO_DIR:-$HOME/reservas-parquei}"
DEPLOY_ROOT="${DEPLOY_ROOT:-$HOME/reservas-deploy}"
STATE_FILE="${STATE_FILE:-${STATE_DIRECTORY:-$DEPLOY_ROOT}/state.json}"
MIN_DISCO_MB="${MIN_DISCO_MB:-3072}"
API="https://api.github.com"

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

SHA=""
log()  { printf '[%s] %s\n' "${SHA:0:7}" "$*"; }
warn() { printf '[%s] AVISO: %s\n' "${SHA:0:7}" "$*" >&2; }
die()  { printf '[%s] ERROR: %s\n' "${SHA:0:7}" "$*" >&2; exit 1; }

: "${GH_TOKEN:?Falta GH_TOKEN (ver deploy/README.md)}"

# Se comprueban por adelantado para fallar con un mensaje entendible en vez
# de a mitad del despliegue. python3 y flock vienen con Ubuntu Server;
# rsync suele hacer falta instalarlo (`apt-get install -y rsync`).
for dep in curl python3 rsync flock docker git; do
  command -v "$dep" >/dev/null 2>&1 || die "Falta '$dep'. Ver deploy/README.md."
done

mkdir -p "$DEPLOY_ROOT"/{releases,rollback,backups,tmp}

# --- Cerrojo -------------------------------------------------------------
# El timer usa OnUnitInactiveSec, así que systemd ya impide solapamiento;
# esto cubre además una ejecución manual mientras el timer está corriendo.
exec 9>"$DEPLOY_ROOT/.deploy.lock"
if ! flock -n 9; then
  echo "Otro despliegue en curso; saliendo."
  exit 0
fi

# --- Precondición: disco ------------------------------------------------
# Va ANTES de descargar nada. Sin este control el modo de fallo es feo:
# build a medias, capas de docker corruptas y un rsync truncado que deja el
# bundle vivo incompleto.
disponible_mb="$(df --output=avail -m "$DEPLOY_ROOT" | tail -1 | tr -d ' ')"
[ "$disponible_mb" -ge "$MIN_DISCO_MB" ] \
  || die "Solo ${disponible_mb}MB libres en $DEPLOY_ROOT (mínimo ${MIN_DISCO_MB}MB)."

api_get() {
  # --retry cubre cortes de red transitorios; un fallo acá ocurre ANTES de
  # tocar producción, así que abortar es seguro.
  curl -fsS --retry 3 --retry-delay 5 --retry-connrefused --max-time 60 \
    -H "Authorization: Bearer $GH_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$1"
}

# jq no está garantizado en el servidor y añadir un repo apt a un bastión
# es más caro que estas cuatro líneas: python3 viene con Ubuntu.
json() { python3 -c "$@"; }

# --- 1. Última corrida verde de la rama ---------------------------------
# event=push es OBLIGATORIO, no cosmético: los runs de pull_request tienen
# como head_sha el commit de merge efímero de GitHub, que no existe en la
# rama — desplegarlo fallaría al hacer checkout.
runs_url="$API/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW/runs?branch=$BRANCH&status=success&event=push&per_page=1"
if ! runs_json="$(api_get "$runs_url" 2>/dev/null)"; then
  die "No se pudo consultar GitHub. Si es 401, el token expiró o fue revocado; si es 404, el token no tiene acceso al repo (¿es un PAT fine-grained? Ver deploy/README.md)."
fi

read -r RUN_ID SHA <<<"$(printf '%s' "$runs_json" | json '
import json, sys
runs = json.load(sys.stdin).get("workflow_runs") or []
if runs:
    print("%s %s" % (runs[0]["id"], runs[0]["head_sha"]))
')" || true

if [ -z "${RUN_ID:-}" ]; then
  echo "Todavía no hay ninguna corrida verde de $WORKFLOW en $BRANCH; nada que desplegar."
  exit 0
fi

# --- 2. ¿Ya está desplegado? --------------------------------------------
if [ "$FORCE" -eq 0 ] && [ -f "$STATE_FILE" ]; then
  ya="$(json '
import json,sys
try: e = json.load(open(sys.argv[1]))
except Exception: e = {}
print("si" if e.get("sha") == sys.argv[2] else "no")
' "$STATE_FILE" "$SHA" 2>/dev/null || echo no)"
  if [ "$ya" = "si" ]; then
    # Silencioso a propósito: es el 99% de las ejecuciones del timer.
    exit 0
  fi
fi

log "Desplegando $SHA (corrida $RUN_ID)."

# --- 3. Artefacto de esa corrida ----------------------------------------
arts_json="$(api_get "$API/repos/$OWNER/$REPO/actions/runs/$RUN_ID/artifacts")"
read -r ART_ID ART_EXPIRADO <<<"$(printf '%s' "$arts_json" | json '
import json, sys
buscado = sys.argv[1]
for a in json.load(sys.stdin).get("artifacts", []):
    if a["name"] == buscado:
        print(a["id"], "si" if a["expired"] else "no")
        break
' "$ARTIFACT")" || true

[ -n "${ART_ID:-}" ] || die "La corrida $RUN_ID no publicó el artefacto '$ARTIFACT'. ¿Se quitó el paso de upload de ci.yml?"
[ "$ART_EXPIRADO" = "no" ] || die "El artefacto de $SHA expiró. Relanzá el workflow en GitHub (Re-run jobs). NO se compila en el servidor a propósito: eso desplegaría un bundle no verificado por CI."

# La descarga es en DOS pasos a propósito. El endpoint responde 302 a una
# URL firmada de Azure; curl reenvía las cabeceras de -H a través del
# redirect y Azure rechaza con 400 ("Only one authentication mechanism
# allowed") al ver el SAS y el Authorization a la vez.
zip_url="$(curl -fsS -o /dev/null -w '%{redirect_url}' \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "$API/repos/$OWNER/$REPO/actions/artifacts/$ART_ID/zip")"
[ -n "$zip_url" ] || die "GitHub no devolvió URL de descarga para el artefacto $ART_ID."

REL="$DEPLOY_ROOT/releases/$SHA"
rm -rf "$REL" && mkdir -p "$REL"
curl -fsS --retry 3 --retry-delay 5 --speed-time 30 --speed-limit 5000 \
  --max-time 600 -o "$DEPLOY_ROOT/tmp/web.zip" "$zip_url"

python3 -c 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' \
  "$DEPLOY_ROOT/tmp/web.zip" "$REL"
rm -f "$DEPLOY_ROOT/tmp/web.zip"

# Última barrera contra el 403 de nginx: si el bundle vino incompleto, se
# aborta ANTES de tocar el que está sirviendo.
for f in index.html main.dart.js flutter_bootstrap.js; do
  [ -s "$REL/$f" ] || die "El artefacto no trae $f; se aborta sin tocar el despliegue vivo."
done

# Los zips de artefacto no preservan permisos POSIX y nginx corre como otro
# usuario dentro del contenedor: sin esto, 403 por archivo.
chmod -R a+rX "$REL"

# --- 4. Checkout en el commit exacto que validó el CI --------------------
cd "$REPO_DIR"
# -uno: build/ y .env están gitignored y siempre "sobran"; lo que importa
# es que no haya cambios en archivos versionados que se perderían.
sucio="$(git status --porcelain --untracked-files=no)"
[ -z "$sucio" ] || die "Árbol de trabajo sucio en $REPO_DIR; se aborta sin tocar nada:"$'\n'"$sucio"

git -c credential.helper= \
    -c credential.helper='!f(){ printf "username=x-access-token\npassword=%s\n" "$GH_TOKEN"; };f' \
    fetch --prune origin "$BRANCH" --quiet

git cat-file -e "${SHA}^{commit}" 2>/dev/null \
  || die "El commit $SHA no existe tras el fetch (¿force-push sobre la rama?)."

PREV_SHA="$(git rev-parse HEAD)"
# `switch` en vez de `reset --hard`: aborta si fuese a pisar algo, en vez de
# destruirlo en silencio. Detached a propósito — este checkout es un
# artefacto de despliegue, no un espacio de trabajo.
git -c advice.detachedHead=false switch --detach "$SHA" --quiet

restaurar_checkout() { git -c advice.detachedHead=false switch --detach "$PREV_SHA" --quiet || true; }

cambio_en() { ! git diff --quiet "$PREV_SHA" "$SHA" -- "$@" 2>/dev/null; }

# --- 5. Respaldo de base solo si el esquema puede moverse ----------------
# Las migraciones corren solas en el arranque de FastAPI. Si ni migrations.py
# ni los modelos cambiaron, ese arranque es un no-op sobre el esquema y el
# dump no aportaría nada: no se hace en cada despliegue de solo-frontend.
if [ "$PREV_SHA" != "$SHA" ] && cambio_en backend/app/migrations.py backend/app/models; then
  log "Cambió el esquema; respaldando la base antes de arrancar."
  dump="$DEPLOY_ROOT/backups/${SHA:0:7}-$(date +%Y%m%d-%H%M%S).dump"
  if docker exec reservas_db pg_dump -U "${PGUSER:-postgres}" -d "${PGDB:-reservas_db}" -Fc > "$dump" 2>/dev/null; then
    log "Respaldo en $dump"
    ls -1t "$DEPLOY_ROOT/backups"/*.dump 2>/dev/null | tail -n +8 | xargs -r rm -f
  else
    rm -f "$dump"
    restaurar_checkout
    die "Falló el pg_dump previo a una migración; se aborta el despliegue."
  fi
fi

# --- 6. Intercambio del bundle web --------------------------------------
# EL PUNTO DELICADO. `flutter_proxy` monta ./app_flutter/build/web como bind
# mount, y un bind mount se resuelve UNA sola vez, al arrancar el contenedor,
# quedando atado al inode del directorio. Si acá se moviera el directorio y
# se pusiera otro, nginx seguiría sirviendo el viejo (ya invisible desde el
# host) para siempre, y ningún `up -d` lo arreglaría porque el contenedor no
# se recrea. Por eso se sincroniza el CONTENIDO, nunca se sustituye el
# directorio.
WEB_DIR="$REPO_DIR/app_flutter/build/web"
mkdir -p "$WEB_DIR"

# Se comprueba ANTES de tocar nada. Si `flutter build web` se corrió alguna
# vez con el contenedor descartable, todo build/ quedó de root (los
# contenedores escriben como root en los volúmenes montados) y este agente,
# que corre sin privilegios, no puede escribir ahí. Sin esta comprobación el
# fallo aparece a mitad del rsync, con decenas de "Permission denied" y el
# despliegue a medias.
if [ ! -w "$WEB_DIR" ]; then
  die "No se puede escribir en $WEB_DIR (dueño: $(stat -c '%U:%G' "$WEB_DIR")). Suele pasar tras compilar con el contenedor descartable, que escribe como root. Corregilo una vez con:
    sudo chown -R \"\$(id -un):\$(id -gn)\" \"$REPO_DIR/app_flutter/build\""
fi

ROLLBACK_DIR="$DEPLOY_ROOT/rollback/web-$(date +%Y%m%d-%H%M%S)"
# --preserve=mode,timestamps en vez de `cp -a`: preservar el DUEÑO exige
# privilegios que este agente no tiene (y no los necesita).
cp -R --preserve=mode,timestamps "$WEB_DIR" "$ROLLBACK_DIR"

# --no-owner --no-group por el mismo motivo: sin ellos, `-a` intenta un
# chgrp por archivo que falla para un usuario sin privilegios. Al agente le
# importa el contenido y los permisos de lectura, no la propiedad.
RSYNC_OPTS=(-a --no-owner --no-group)

# Los puntos de entrada van al final: referencian los hashes del build nuevo,
# así que copiarlos primero abriría una ventana en la que el navegador pide
# assets que todavía no existen.
rsync "${RSYNC_OPTS[@]}" --delete-after --exclude='index.html' --exclude='flutter_bootstrap.js' "$REL"/ "$WEB_DIR"/
rsync "${RSYNC_OPTS[@]}" "$REL"/index.html "$WEB_DIR"/
[ -f "$REL/flutter_bootstrap.js" ] && rsync "${RSYNC_OPTS[@]}" "$REL"/flutter_bootstrap.js "$WEB_DIR"/
chmod -R a+rX "$WEB_DIR"

# --- 7. Converger el stack ----------------------------------------------
REBUILD=0
if [ "$PREV_SHA" != "$SHA" ] && cambio_en backend docker-compose.yml; then REBUILD=1; fi

# Sin --remove-orphans a propósito: eliminaría contenedores de este mismo
# proyecto que ya no están en el compose, y eso debe ser una decisión
# deliberada y puntual, no el efecto colateral de un bucle cada 3 minutos.
if [ "$REBUILD" -eq 1 ]; then
  log "Cambió backend/ o docker-compose.yml; reconstruyendo."
  docker compose build backend
  docker compose up -d --wait --wait-timeout 300 backend
  # OBLIGATORIO tras recrear el backend: nginx resuelve el nombre `backend`
  # al cargar la config y cachea la IP (no hay directiva `resolver` en
  # nginx.conf). Un contenedor nuevo suele recibir otra IP, y el proxy
  # quedaría con 502 permanente en /api mientras el frontend carga bien.
  docker compose restart flutter_proxy
else
  # Aun sin recrear el backend hay que reiniciar el proxy: el bundle cambió
  # y, si el directorio fue recreado alguna vez, el mount podría estar
  # apuntando a un inode viejo.
  docker compose restart flutter_proxy
fi
docker compose up -d --wait --wait-timeout 180

# --- 8. Verificación ----------------------------------------------------
# El puerto se le pregunta a compose en vez de leer el .env (que tiene
# secretos) o hardcodearlo.
PORT="$(docker compose port flutter_proxy 80 | sed 's/.*://')"
BASE="http://127.0.0.1:${PORT:-8091}"

salud() {
  curl -fsS --max-time 10 "$BASE/health" | grep -q '"status":"ok"' || return 1
  [ "$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 "$BASE/")" = "200" ] || return 1
  curl -fsS --max-time 10 -o /dev/null "$BASE/main.dart.js" || return 1
  # 401 es la respuesta CORRECTA de un endpoint autenticado sin cookie:
  # distingue "el backend responde y /api/ enruta bien" de un 502 del proxy
  # (IP cacheada) o un 404 de nginx.
  [ "$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 "$BASE/api/usuarios/me")" = "401" ] || return 1
}

ok=0
for _ in $(seq 1 12); do salud && { ok=1; break; }; sleep 5; done

if [ "$ok" -ne 1 ]; then
  warn "El health check falló; revirtiendo a $PREV_SHA."
  rsync "${RSYNC_OPTS[@]}" --delete-after "$ROLLBACK_DIR"/ "$WEB_DIR"/
  restaurar_checkout
  if [ "$REBUILD" -eq 1 ]; then
    docker compose build backend && docker compose up -d --wait --wait-timeout 300 backend || true
  fi
  docker compose restart flutter_proxy || true
  # Se registra el SHA fallido para NO reintentarlo cada 3 minutos: sin
  # esto, un commit verde pero roto en runtime genera un bucle infinito de
  # despliegue-rollback con el proxy reiniciándose sin parar.
  printf '{"sha":"%s","run_id":%s,"previous_sha":"%s","deployed_at":"%s","status":"failed","error":"health check"}\n' \
    "$SHA" "$RUN_ID" "$PREV_SHA" "$(date -Is)" > "$STATE_FILE.tmp"
  mv -f "$STATE_FILE.tmp" "$STATE_FILE"
  die "Despliegue revertido. Se sirve de nuevo $PREV_SHA."
fi

# --- 9. Estado y poda ---------------------------------------------------
printf '{"sha":"%s","run_id":%s,"previous_sha":"%s","deployed_at":"%s","backend_rebuilt":%s,"status":"ok"}\n' \
  "$SHA" "$RUN_ID" "$PREV_SHA" "$(date -Is)" "$([ "$REBUILD" -eq 1 ] && echo true || echo false)" \
  > "$STATE_FILE.tmp"
mv -f "$STATE_FILE.tmp" "$STATE_FILE"

ls -1dt "$DEPLOY_ROOT/releases"/* 2>/dev/null | tail -n +6 | xargs -r rm -rf
ls -1dt "$DEPLOY_ROOT/rollback"/* 2>/dev/null | tail -n +4 | xargs -r rm -rf

log "Desplegado correctamente en $BASE"
