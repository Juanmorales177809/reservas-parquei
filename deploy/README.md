# Despliegue continuo al servidor (modelo *pull*)

## Por qué este modelo y no el habitual

El CD clásico —GitHub Actions se conecta por SSH y despliega— **no es posible aquí**, por dos razones independientes:

| Restricción | Consecuencia |
| --- | --- |
| El servidor tiene IP privada, sin entrada desde internet | Los runners de GitHub viven en la nube y no pueden alcanzarlo |
| Quien opera esto tiene `push` pero **no** `admin` sobre el repo | No puede registrar un runner self-hosted ni crear *secrets*: ambas cosas exigen admin |

Se invierte la dirección: **el servidor consulta a GitHub, GitHub nunca entra**. Solo hace falta salida a internet y un token de lectura. No se abre ningún puerto.

## Cómo funciona

```
GitHub Actions (ubuntu-latest)              Servidor (IP privada)
  push a la rama → ci.yml                     timer systemd (cada 3 min)
    backend  ─┐                                     │
    flutter  ─┼→ artefacto "flutter-web"            │ curl → api.github.com
    e2e      ─┘   (lo descarga, no recompila)       │   (solo salida)
                                                     ▼
                                         /usr/local/bin/reservas-deploy
                                           1. última corrida VERDE de la rama
                                           2. ¿ese SHA ya está desplegado? → salir
                                           3. baja y descomprime el artefacto
                                           4. git switch --detach <SHA>
                                           5. rsync in-place al bind-mount
                                           6. rebuild backend solo si hizo falta
                                           7. health check → rollback si falla
```

La pieza que lo hace barato: el job `flutter` de CI ya compilaba `build/web` y lo descartaba. Ahora lo publica. El servidor **no compila Flutter**: bajarse ~1 GB de SDK y compilar 5 minutos en cada despliegue era el costo real del proceso manual (y se colgó dos veces en el primer intento). Ahora es una descarga de segundos.

## Instalación

### 1. Crear el token

Tiene que ser un **PAT clásico**, no *fine-grained*. No es preferencia: los fine-grained solo apuntan a repos cuyo propietario sea tu cuenta o una organización tuya, y este repo es de otra cuenta personal donde sos colaborador. Si usás uno fine-grained, la API responde **404** (GitHub no distingue "no existe" de "no autorizado" en repos privados) y vas a perder una tarde depurándolo.

En GitHub → Settings → Developer settings → Personal access tokens → **Tokens (classic)** → Generate new token:

- Scope: solo **`repo`**. Cubre a la vez el `git fetch` del repo privado y la lectura de corridas y artefactos. No hace falta `workflow` (eso es para *modificar* archivos de workflow).
- Expiración: anotala. Cuando venza, el agente registra `ERROR: credencial rechazada (401)` en el journal y deja de desplegar — no rompe lo que ya está sirviendo.

```bash
sudo mkdir -p /etc/reservas-deploy
sudo tee /etc/reservas-deploy/deploy.env >/dev/null <<'EOF'
GH_TOKEN=ghp_TU_TOKEN_ACA
EOF
sudo chmod 600 /etc/reservas-deploy/deploy.env
sudo chown root:root /etc/reservas-deploy/deploy.env
```

`root:root` y no el usuario de despliegue: systemd lee `EnvironmentFile=` **como root, antes** de bajar privilegios a `User=`. El token llega al proceso, pero el archivo en disco no es legible por nadie más.

### 2. Instalar el script y las unidades

```bash
cd ~/reservas-parquei
sudo install -m 0755 -o root -g root deploy/reservas-deploy.sh /usr/local/bin/reservas-deploy
sudo install -m 0644 deploy/systemd/reservas-deploy.service /etc/systemd/system/
sudo install -m 0644 deploy/systemd/reservas-deploy.timer /etc/systemd/system/
sudo apt-get install -y rsync
sudo systemctl daemon-reload
```

Si el usuario del servidor no es `bastion`, ajustá `User=`, `Group=`, `Environment=HOME=` y `WorkingDirectory=` en el `.service` antes del `daemon-reload`.

### 3. Dar la propiedad de `build/` al usuario de despliegue

Si alguna vez se compiló la Web en el servidor con el contenedor descartable, todo `app_flutter/build/` quedó de **root**: los contenedores escriben como root en los volúmenes montados. El agente corre sin privilegios y no podría escribir ahí.

```bash
sudo chown -R "$(id -un):$(id -gn)" ~/reservas-parquei/app_flutter/build
```

El agente comprueba esto por adelantado y aborta con este mismo comando en el mensaje si detecta el problema, sin tocar el bundle que está sirviendo.

### 4. Probarlo A MANO antes de activar el timer

```bash
sudo systemctl start reservas-deploy.service && journalctl -u reservas-deploy -n 50 --no-pager
```

Debe terminar en `Desplegado correctamente en http://127.0.0.1:8091`. Si algo falla, falla **sin tocar** lo que está sirviendo (todas las validaciones ocurren antes del primer efecto secundario).

### 5. Activar el timer

```bash
sudo systemctl enable --now reservas-deploy.timer && systemctl list-timers reservas-deploy.timer
```

## Operación

```bash
journalctl -u reservas-deploy -f              # seguir en vivo
journalctl -u reservas-deploy -S -7d -p warning   # solo problemas de la semana
cat ~/reservas-deploy/state.json              # qué está desplegado ahora
sudo systemctl start reservas-deploy.service  # forzar un ciclo ya
sudo -u bastion GH_TOKEN=... /usr/local/bin/reservas-deploy --force   # redesplegar el mismo SHA
```

## ⚠️ El agente no se actualiza solo

`/usr/local/bin/reservas-deploy` es una **copia** instalada a mano. El agente despliega el checkout del repo, pero no se reemplaza a sí mismo, así que un cambio en `deploy/reservas-deploy.sh` **no surte efecto hasta reinstalarlo**:

```bash
sudo install -m 0755 -o root -g root ~/reservas-parquei/deploy/reservas-deploy.sh /usr/local/bin/reservas-deploy
```

Esperar primero a que el agente haya desplegado el commit que trae el cambio (así el archivo ya está en el checkout), o hacer `git switch feature/soV0.1 && git pull` a mano.

Es deliberado y no un descuido: si el servicio ejecutara el script directamente desde el checkout, una versión rota del agente se autodesplegaría y podría dejar el despliegue inservible sin forma cómoda de volver atrás. Con la copia instalada, el agente que corre siempre es uno que alguien puso ahí a conciencia. El costo es este paso manual, poco frecuente.

Lo mismo aplica a las unidades de systemd (`.service` / `.timer`): si cambian, hay que reinstalarlas y hacer `sudo systemctl daemon-reload`.

## Ejercitar el rollback

Un rollback que nunca se probó es una suposición, no un mecanismo. No se puede provocar el fallo "de verdad" sin romper el stack (parar el backend a mano no sirve: `docker compose up -d` lo levanta antes de llegar al health check), así que el script trae una válvula explícita.

```bash
sudo systemctl stop reservas-deploy.timer     # que no interfiera a mitad
sudo -u bastion DEPLOY_FORZAR_FALLO_SALUD=1 \
     GH_TOKEN="$(sudo sed -n 's/^GH_TOKEN=//p' /etc/reservas-deploy/deploy.env)" \
     /usr/local/bin/reservas-deploy --force
```

Debe: sincronizar el bundle, fallar el health check, **restaurar el bundle anterior**, volver el checkout al commit previo, reiniciar el proxy y terminar con `Despliegue revertido`. Comprobar después:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8091/   # 200: el sitio sigue en pie
cat ~/reservas-deploy/state.json                                   # status: "failed"
```

Para recuperarse hace falta `--force`: un SHA registrado como fallido **no se reintenta solo** (ver más abajo). Reactivar el timer al terminar:

```bash
sudo -u bastion GH_TOKEN="$(sudo sed -n 's/^GH_TOKEN=//p' /etc/reservas-deploy/deploy.env)" \
     /usr/local/bin/reservas-deploy --force
sudo systemctl start reservas-deploy.timer
```

## Decisiones que parecen raras y no lo son

**El agente nunca compila Flutter.** Si el artefacto expiró (14 días), aborta y te pide relanzar el workflow en GitHub. Compilar en el servidor como respaldo desplegaría un bundle *no verificado por CI*, que es justo lo que este diseño evita.

**Se sincroniza el contenido de `build/web`, nunca se reemplaza el directorio.** El bind-mount de `flutter_proxy` se resuelve una sola vez, al arrancar el contenedor, y queda atado al *inode*. Mover el directorio dejaría a nginx sirviendo el viejo para siempre, sin que ningún `up -d` lo corrija.

**Se reinicia `flutter_proxy` siempre que se recrea el backend.** `nginx.conf` hace `proxy_pass http://backend:8000/` sin directiva `resolver`, así que nginx resuelve ese nombre al cargar la config y cachea la IP. Un contenedor de backend nuevo suele recibir otra IP: sin el reinicio quedás con **502 permanente en `/api` mientras el frontend carga perfecto**, que es de los fallos más difíciles de diagnosticar.

**No se usa `--remove-orphans`.** Solo afecta a contenedores del mismo proyecto compose (los otros stacks del host están a salvo), pero eliminaría contenedores obsoletos de *este* proyecto. Eso debe ser una decisión puntual y deliberada, no el efecto colateral de un bucle que corre cada 3 minutos.

**El SHA que falla el health check se registra como fallido y no se reintenta.** Sin eso, un commit verde pero roto en runtime generaría un bucle infinito de despliegue-rollback cada 3 minutos, reiniciando el proxy sin parar. Solo un commit nuevo dispara un intento nuevo.

**El respaldo de base es condicional.** Solo se hace `pg_dump` si cambiaron `backend/app/migrations.py` o `backend/app/models` entre el commit desplegado y el nuevo — que es cuando el arranque de FastAPI puede mover el esquema. Un despliegue de solo-frontend no lo dispara. El rollback **nunca** restaura la base: las migraciones son aditivas e idempotentes, así que el código anterior convive con el esquema nuevo; revertir el esquema sería más destructivo que dejarlo. El dump existe para que una persona pueda recuperarse de un desastre, no para que el script lo intente.

**Se usa `git switch --detach`, nunca `reset --hard`.** `switch` aborta si fuese a pisar cambios locales; `reset --hard` los destruye en silencio. Y si el árbol está sucio, el agente se planta y avisa en vez de forzar.

## pgAdmin ya no se publica en la red

`docker-compose.yml` publicaba pgAdmin en `8085` sobre **todas** las interfaces, con credenciales que ni siquiera figuraban en `.env.example`: cualquiera en la red del servidor llegaba a una consola de administración de la base con datos reales. Ahora se ata a loopback por defecto (`PGADMIN_BIND=127.0.0.1`).

Al aplicar este cambio en un servidor donde pgAdmin ya corría, hay que recrear el contenedor para que tome el nuevo mapeo:

```bash
docker compose up -d --force-recreate pgadmin
docker compose port pgadmin 5050    # debe imprimir 127.0.0.1:8085, no 0.0.0.0:8085
```

Para entrar desde otra máquina, túnel SSH:

```bash
ssh -L 8085:127.0.0.1:8085 usuario@servidor
```

y abrir `http://127.0.0.1:8085` en el navegador local.

## Limitaciones conocidas

- **Solo despliega la rama configurada** (`BRANCH`, por defecto `feature/soV0.1`).
- **Latencia**: hasta 3 minutos de poll + ~7 minutos de CI.
- **El E2E real no corre en CI** (necesita un runner Windows con Visual Studio), así que "verde" significa `pytest` + `flutter analyze` + `flutter test` + smoke del bundle, no el flujo completo de usuario.
