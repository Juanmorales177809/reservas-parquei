#!/bin/sh
# Prepara la base de datos antes de que arranque el backend. Lo ejecuta el servicio `migrar` de docker-compose.yml.
#
# - Base vacía (servidor nuevo): construye el esquema desde cero, en el orden exacto que documenta
#   backend/tests/conftest.py, carga los catálogos y, si CARGAR_DATOS_LIA=true, los laboratorios, cargos y
#   equipos de LIA (backend/seeds/).
# - Base con esquema (un despliegue que ya corrió): no la reconstruye jamás; solo aplica las migraciones
#   posteriores a la línea base que todavía no consten en public.schema_migrations.
#
# Nunca borra datos. Corrida dos veces seguidas, la segunda no cambia nada.
#
# Variables (las fija docker-compose.yml): PGHOST, PGUSER, PGPASSWORD, PGDATABASE, CARGAR_DATOS_LIA, ENTORNO,
# JWT_SECRET.

set -eu
export PGCLIENTENCODING=UTF8

M=/migraciones
S=/semillas

falla() {
    echo "ERROR: $1" >&2
    exit 1
}

# En producción no se arranca con los valores de ejemplo.
if [ "${ENTORNO:-desarrollo}" = "produccion" ]; then
    case "${JWT_SECRET:-}" in
        "" | cambiar*) falla "JWT_SECRET vacío o de ejemplo. Genere uno: python -c \"import secrets; print(secrets.token_urlsafe(64))\"" ;;
    esac
    [ "${#JWT_SECRET}" -ge 32 ] || falla "JWT_SECRET debe tener al menos 32 caracteres."
    [ "${PGPASSWORD:-}" != "postgres" ] || falla "POSTGRES_PASSWORD no puede ser 'postgres' en producción."
    [ -n "${PGPASSWORD:-}" ] || falla "POSTGRES_PASSWORD vacío."
fi

psqlx() { psql -v ON_ERROR_STOP=1 -q "$@"; }
consulta() { psql -tA -c "$1"; }

existe_esquema=$(consulta "select to_regclass('auth.cuentas') is not null")

if [ "$existe_esquema" = "t" ]; then
    echo "La base ya tiene esquema: no se reconstruye. Solo se aplican las migraciones pendientes."
else
    echo "Base vacía: se construye el esquema desde cero."
    for f in \
        reconstruccion/000_base_compartida.sql \
        reconstruccion/001_shared_postgres.sql \
        reconstruccion/001b_transicion_cuenta.sql \
        002_reservas_objetivo.sql \
        reconstruccion/003_limpieza_heredada.sql \
        011_gobierno.sql \
        010_auth_objetivo.sql \
        seeds/catalogos_reservas.sql \
        seeds/permisos.sql \
        004_recursos.sql \
        005_investigacion.sql \
        006_administration.sql \
        007_notificaciones.sql \
        003_reservas_referencias_externas.sql \
        009_concurrencia.sql \
        seeds/tipos_evento.sql \
        seeds/tipos_evento_auth.sql \
        008_identidades.sql \
        012_importacion_resultados_datos.sql
    do
        echo "  $f"
        psqlx -f "$M/$f"
    done

    if [ "${CARGAR_DATOS_LIA:-true}" = "true" ]; then
        echo "Cargando los laboratorios, cargos y equipos de LIA."
        psqlx -f "$S/lia_laboratorios_y_cargos.sql"
        psqlx -f "$S/lia_equipos.sql"
    fi
fi

# Migraciones posteriores a la línea base. Cada una se registra en public.schema_migrations al aplicarse.
for n in 013_corregir_textos_tipos_evento 014_cuenta_administrador; do
    aplicada=$(consulta "select exists(select 1 from public.schema_migrations where nombre = '$n')")
    if [ "$aplicada" = "t" ]; then
        echo "  $n: ya aplicada"
    else
        echo "  $n"
        psqlx -f "$M/$n.sql"
    fi
done

echo "Base lista."
