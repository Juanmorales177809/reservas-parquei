"""Servicio de reports (API-19, API-20): agregados de solo lectura.

No modifica nada (RN-REP-02/06, RN-EST-04): calcula sobre filas existentes.
Horas coherentes con fechas y horarios registrados (RN-OCU-02); sin horario
definido no hay porcentaje, nunca un cero (RN-OCU-06).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from app.core.authz import exigir_permiso, resolver_rol
from app.core.deps import ContextoAutenticado
from app.core.errors import SolicitudInvalida, Validacion
from app.modules.reports import repository as repo

_ESTADOS_OCUPACION = ("APROBADA", "EN_EJECUCION", "FINALIZADA")
_DIMENSIONES = ("laboratorio", "espacio", "recurso", "proyecto", "semillero")
_TIPOS_EXPORTACION = ("ocupacion", "solicitudes", "lista-espera")
_ESTADOS_SOLICITUD = ("solicitada", "aprobada", "rechazada", "en_ejecucion", "finalizada", "cancelada")


def _parse_periodo(desde: str | None, hasta: str | None, *, obligatorio: bool) -> tuple[date | None, date | None]:
    if desde is None or hasta is None:
        if obligatorio:
            raise Validacion("desde y hasta son obligatorios en este reporte.")
        return None, None
    d0, d1 = date.fromisoformat(desde), date.fromisoformat(hasta)
    if d0 > d1:
        raise Validacion("desde no puede ser posterior a hasta.")
    return d0, d1


def _unidades_en_ambito(db, contexto: ContextoAutenticado, id_unidad: int | None) -> list[int] | None:
    """None = todas (admin global sin filtro). Técnico: solo la suya."""
    exigir_permiso(db, contexto.id_cuenta, "reportes.consultar", id_unidad=id_unidad)
    rol = resolver_rol(db, contexto.id_cuenta)
    if rol.unidades_autorizadas == "GLOBAL":
        return None if id_unidad is None else [id_unidad]
    propia = rol.unidades_autorizadas[0]
    return [propia]


def _horas_franja(fecha: date, h0: time, h1: time, desde: date, hasta: date) -> float:
    if fecha < desde or fecha > hasta:
        return 0.0
    minutos = (h1.hour * 60 + h1.minute) - (h0.hour * 60 + h0.minute)
    return max(0.0, minutos / 60)


def _dias_solapados(d0: date, d1: date, desde: date, hasta: date) -> int:
    inicio, fin = max(d0, desde), min(d1, hasta)
    return max(0, (fin - inicio).days + 1)


def _horas_atencion(db, id_unidad: int, desde: date, hasta: date) -> float | None:
    """Horas de atención con las versiones vigentes entonces (RN-LAB-08).
    None si ninguna versión cubre el periodo (RN-OCU-06)."""
    versiones = repo.historico_horario(db, id_unidad)
    if not versiones:
        return None
    total = 0.0
    cubierto = False
    dia = desde
    while dia <= hasta:
        version = next(
            (v for v in versiones
             if v.vigente_desde.date() <= dia and (v.vigente_hasta is None or dia < v.vigente_hasta.date())),
            None,
        )
        if version is not None:
            cubierto = True
            dias = version.dias_atencion or []
            if (dia.weekday() + 1) % 7 in dias:
                apertura = version.hora_apertura.hour * 60 + version.hora_apertura.minute
                cierre = version.hora_cierre.hour * 60 + version.hora_cierre.minute
                total += max(0.0, (cierre - apertura) / 60)
        dia += timedelta(days=1)
    return total if cubierto else None


def _horas_reserva_por_tipo(db, reserva_id: int, tipo: str, desde: date, hasta: date) -> float:
    if tipo == "ESPACIO":
        d = repo.detalles_espacio(db, [reserva_id]).get(reserva_id)
        return _horas_franja(d.fecha, d.hora_inicio, d.hora_fin, desde, hasta) if d else 0.0
    if tipo == "RECURSO_INTERNO":
        d = repo.detalles_internos(db, [reserva_id]).get(reserva_id)
        return _horas_franja(d.fecha, d.hora_inicio, d.hora_fin, desde, hasta) if d else 0.0
    if tipo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        getter = repo.detalles_campus if tipo == "RECURSO_CAMPUS" else repo.detalles_externos
        d = getter(db, [reserva_id]).get(reserva_id)
        return _dias_solapados(d.fecha_salida, d.fecha_devolucion_estimada, desde, hasta) * 24.0 if d else 0.0
    return 0.0


def _porcentaje(reservadas: float, disponibles: float | None) -> float | None:
    if disponibles is None or disponibles <= 0:
        return None
    return round(reservadas / disponibles * 100, 1)


def _solapa_periodo(db, reserva_id: int, tipo: str, d0: date | None, d1: date | None) -> bool:
    """Demanda del periodo: la franja se cruza con [desde, hasta].
    Lista de espera no tiene fechas: siempre suma."""
    if d0 is None:
        return True
    if tipo == "ESPACIO":
        d = repo.detalles_espacio(db, [reserva_id]).get(reserva_id)
        return d is not None and d0 <= d.fecha <= d1
    if tipo == "RECURSO_INTERNO":
        d = repo.detalles_internos(db, [reserva_id]).get(reserva_id)
        return d is not None and d0 <= d.fecha <= d1
    if tipo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        getter = repo.detalles_campus if tipo == "RECURSO_CAMPUS" else repo.detalles_externos
        d = getter(db, [reserva_id]).get(reserva_id)
        return d is not None and d.fecha_salida <= d1 and d.fecha_devolucion_estimada >= d0
    return True


def ocupacion(db, dimension: str, desde: str | None, hasta: str | None, filtros: dict, contexto: ContextoAutenticado, *, pagina=1, tamano=20):
    if dimension not in _DIMENSIONES:
        raise SolicitudInvalida("dimension debe ser una de: " + ", ".join(_DIMENSIONES) + ".")
    d0, d1 = _parse_periodo(desde, hasta, obligatorio=True)
    unidades = _unidades_en_ambito(db, contexto, filtros.get("id_unidad"))
    filas = repo.reservas_base(db, unidades, list(_ESTADOS_OCUPACION))
    ids = [r.id for r, _, _ in filas]
    contextos = repo.contextos_de(db, ids)
    asignaciones = repo.asignaciones_activas(db, ids)

    datos: list[dict] = []
    if dimension == "espacio":
        espacios = repo.espacios_de(db, unidades, filtros.get("espacio_id"))
        det = repo.detalles_espacio(db, ids)
        por_espacio: dict[int, float] = {}
        for r, tipo, _ in filas:
            if tipo != "ESPACIO":
                continue
            d = det.get(r.id)
            if d is None or (filtros.get("espacio_id") is not None and d.espacio_id != filtros["espacio_id"]):
                continue
            por_espacio[d.espacio_id] = por_espacio.get(d.espacio_id, 0.0) + _horas_franja(d.fecha, d.hora_inicio, d.hora_fin, d0, d1)
        for e in espacios:
            disp = _horas_atencion(db, e.id_unidad, d0, d1)
            res = por_espacio.get(e.id, 0.0)
            datos.append({
                "espacio_id": e.id, "nombre": e.nombre, "id_unidad": e.id_unidad,
                "horas_reservadas": round(res, 2), "horas_disponibles": disp,
                "porcentaje_ocupacion": _porcentaje(res, disp),
            })
    elif dimension == "recurso":
        recursos = repo.recursos_de(db, unidades, filtros.get("recurso_id"))
        duracion = (d1 - d0).days + 1
        for rec in recursos:
            asignadas = 0.0
            uso = 0.0
            for r, tipo, estado in filas:
                for a in asignaciones.get(r.id, []):
                    if a.recurso_id != rec.id:
                        continue
                    h = _horas_reserva_por_tipo(db, r.id, tipo, d0, d1)
                    asignadas += h
                    if estado == "FINALIZADA":
                        uso += h
            base = duracion * 24.0
            datos.append({
                "recurso_id": rec.id, "nombre": repo.nombre_recurso(db, rec.id), "id_unidad": rec.id_unidad,
                "horas_reservadas": round(asignadas, 2), "horas_uso": round(uso, 2),
                "porcentaje_ocupacion": _porcentaje(asignadas, base),
            })
    elif dimension == "laboratorio":
        for u in repo.unidades(db, unidades):
            res = sum(
                _horas_reserva_por_tipo(db, r.id, tipo, d0, d1)
                for r, tipo, _ in filas if r.id_unidad == u.id_unidad
            )
            disp = _horas_atencion(db, u.id_unidad, d0, d1)
            datos.append({
                "id_unidad": u.id_unidad, "nombre": u.nombre,
                "horas_reservadas": round(res, 2), "horas_disponibles": disp,
                "porcentaje_ocupacion": _porcentaje(res, disp),
            })
    else:
        es_proyecto = dimension == "proyecto"
        entidades = repo.proyectos_de(db, filtros.get("proyecto_id")) if es_proyecto else repo.semilleros_de(db, filtros.get("semillero_id"))
        clave_filtro = filtros.get("proyecto_id" if es_proyecto else "semillero_id")
        for ent in entidades:
            eid = ent.id_proyecto if es_proyecto else ent.id_semillero
            if clave_filtro is not None and eid != clave_filtro:
                continue
            total = 0.0
            for r, tipo, _ in filas:
                ctx = contextos.get(r.id)
                if ctx is None:
                    continue
                eid_ctx = ctx.proyecto_id if es_proyecto else ctx.semillero_id
                if eid_ctx == eid:
                    total += _horas_reserva_por_tipo(db, r.id, tipo, d0, d1)
            datos.append({
                ("proyecto_id" if es_proyecto else "semillero_id"): eid,
                "nombre": ent.nombre, "horas_reservadas": round(total, 2),
            })

    datos.sort(key=lambda d: tuple(d.get(k) for k in ("id_unidad", "espacio_id", "recurso_id", "proyecto_id", "semillero_id") if k in d))
    total = len(datos)
    resumen = {"dimension": dimension, "desde": d0.isoformat(), "hasta": d1.isoformat(),
               "filtros": {k: v for k, v in filtros.items() if v is not None}}
    return resumen, datos[(pagina - 1) * tamano: pagina * tamano], total


def solicitudes(db, dimension: str, desde: str | None, hasta: str | None, filtros: dict, contexto: ContextoAutenticado, *, pagina=1, tamano=20):
    if dimension not in ("laboratorio",):
        raise SolicitudInvalida("solicitudes solo admite dimension 'laboratorio'.")
    d0, d1 = _parse_periodo(desde, hasta, obligatorio=False)
    if (d0 is None) != (d1 is None):
        raise Validacion("desde y hasta deben venir juntos.")
    if d0 is not None and d0 > d1:
        raise Validacion("desde no puede ser posterior a hasta.")
    unidades = _unidades_en_ambito(db, contexto, filtros.get("id_unidad"))
    filas = repo.reservas_base(db, unidades, None)
    conteos: dict[int, dict] = {}
    for r, tipo, estado in filas:
        if not _solapa_periodo(db, r.id, tipo, d0, d1):
            continue
        unidad = conteos.setdefault(r.id_unidad, {})
        unidad[estado.lower()] = unidad.get(estado.lower(), 0) + 1
    datos = []
    for u in repo.unidades(db, unidades):
        fila = {"id_unidad": u.id_unidad, "nombre": u.nombre}
        for clave in _ESTADOS_SOLICITUD:
            fila[clave] = conteos.get(u.id_unidad, {}).get(clave, 0)
        datos.append(fila)
    total = len(datos)
    resumen = {"dimension": dimension,
               "desde": d0.isoformat() if d0 else None, "hasta": d1.isoformat() if d1 else None,
               "filtros": {k: v for k, v in filtros.items() if v is not None}}
    return resumen, datos[(pagina - 1) * tamano: pagina * tamano], total


def lista_espera(db, desde: str | None, hasta: str | None, filtros: dict, contexto: ContextoAutenticado, *, pagina=1, tamano=20):
    d0, d1 = _parse_periodo(desde, hasta, obligatorio=True)
    unidades = _unidades_en_ambito(db, contexto, filtros.get("id_unidad"))
    agregados = {uid: (n, float(horas)) for uid, n, horas in repo.lista_espera_agregada(db, unidades, d0, d1)}
    datos = []
    for u in repo.unidades(db, unidades):
        n, horas = agregados.get(u.id_unidad, (0, 0.0))
        datos.append({"id_unidad": u.id_unidad, "nombre": u.nombre, "reservas": n, "horas_ejecucion": float(horas)})
    total = len(datos)
    resumen = {"desde": d0.isoformat(), "hasta": d1.isoformat(),
               "filtros": {k: v for k, v in filtros.items() if v is not None}}
    return resumen, datos[(pagina - 1) * tamano: pagina * tamano], total


_COLUMNAS = {
    "ocupacion": ("dimension",),
    "solicitudes": ("id_unidad", "nombre") + _ESTADOS_SOLICITUD,
    "lista-espera": ("id_unidad", "nombre", "reservas", "horas_ejecucion"),
}


def exportar(db, tipo: str, dimension: str | None, desde: str | None, hasta: str | None, filtros: dict, formato: str, contexto: ContextoAutenticado) -> tuple[bytes, str, str]:
    import csv as _csv
    import io as _io

    if tipo not in _TIPOS_EXPORTACION:
        raise SolicitudInvalida("tipo debe ser 'ocupacion', 'solicitudes' o 'lista-espera'.")
    if formato not in ("csv", "excel"):
        raise SolicitudInvalida("formato debe ser 'csv' o 'excel'.")
    if tipo == "ocupacion":
        resumen, datos, _ = ocupacion(db, dimension or "laboratorio", desde, hasta, filtros, contexto, pagina=1, tamano=10**9)
        columnas = sorted({k for d in datos for k in d.keys()})
    elif tipo == "solicitudes":
        resumen, datos, _ = solicitudes(db, dimension or "laboratorio", desde, hasta, filtros, contexto, pagina=1, tamano=10**9)
        columnas = list(_COLUMNAS["solicitudes"])
    else:
        resumen, datos, _ = lista_espera(db, desde, hasta, filtros, contexto, pagina=1, tamano=10**9)
        columnas = list(_COLUMNAS["lista-espera"])

    meta = [("dimension", resumen.get("dimension") or ""), ("desde", resumen.get("desde") or ""),
            ("hasta", resumen.get("hasta") or ""),
            ("filtros", ";".join(f"{k}={v}" for k, v in resumen.get("filtros", {}).items()))]
    if formato == "csv":
        buffer = _io.StringIO()
        for k, v in meta:
            buffer.write(f"# {k}: {v}\n")
        escritor = _csv.writer(buffer)
        escritor.writerow(columnas)
        for d in datos:
            escritor.writerow([d.get(c) for c in columnas])
        return buffer.getvalue().encode("utf-8"), "text/csv", f"reporte-{tipo}.csv"

    import openpyxl

    libro = openpyxl.Workbook()
    hoja = libro.active
    for k, v in meta:
        hoja.append([k, v])
    hoja.append([])
    hoja.append(list(columnas))
    for d in datos:
        hoja.append([d.get(c) if d.get(c) is not None else "" for c in columnas])
    buffer = _io.BytesIO()
    libro.save(buffer)
    return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"reporte-{tipo}.xlsx"


def _periodo_previo(d0: date, d1: date) -> tuple[date, date]:
    """Igual duración que termina el día anterior a `desde` (§3.4)."""
    duracion = (d1 - d0).days + 1
    hasta_prev = d0 - timedelta(days=1)
    return hasta_prev - timedelta(days=duracion - 1), hasta_prev


def resumen(db, desde: str | None, hasta: str | None, filtros: dict, contexto: ContextoAutenticado) -> dict:
    """API-20 §3.4: indicadores y distribuciones del periodo en una sola consulta.

    No introduce cálculos propios: reutiliza demanda (`solicitudes`, RN-OCU-05),
    uso (`ocupacion`, RN-OCU-04), horario histórico (RN-LAB-08) y `null` sin
    horario (RN-OCU-06). Solo lectura (RN-REP-02).
    """
    from math import ceil as _ceil

    d0, d1 = _parse_periodo(desde, hasta, obligatorio=True)
    assert d0 is not None and d1 is not None
    d0p, d1p = _periodo_previo(d0, d1)
    unidades = _unidades_en_ambito(db, contexto, filtros.get("id_unidad"))
    filas = repo.reservas_base(db, unidades, None)
    ids = [r.id for r, _, _ in filas]
    det_esp = repo.detalles_espacio(db, ids)
    det_int = repo.detalles_internos(db, ids)
    det_cam = repo.detalles_campus(db, ids)
    det_ext = repo.detalles_externos(db, ids)
    asign = repo.asignaciones_activas(db, ids)

    def _franja(rid: int, tipo: str):
        if tipo == "ESPACIO":
            d = det_esp.get(rid)
            return ("fecha", d.fecha, d.hora_inicio, d.hora_fin) if d else None
        if tipo == "RECURSO_INTERNO":
            d = det_int.get(rid)
            return ("fecha", d.fecha, d.hora_inicio, d.hora_fin) if d else None
        if tipo == "RECURSO_CAMPUS":
            d = det_cam.get(rid)
            return ("rango", d.fecha_salida, d.fecha_devolucion_estimada) if d else None
        if tipo == "RECURSO_EXTERNO":
            d = det_ext.get(rid)
            return ("rango", d.fecha_salida, d.fecha_devolucion_estimada) if d else None
        return None

    def _cruza(tipo: str, rid: int, a: date, b: date) -> bool:
        f = _franja(rid, tipo)
        if f is None:
            return True  # lista de espera: sin fecha, siempre suma
        if f[0] == "fecha":
            return a <= f[1] <= b
        return f[1] <= b and f[2] >= a

    def _horas(tipo: str, rid: int, a: date, b: date) -> float:
        f = _franja(rid, tipo)
        if f is None:
            return 0.0
        if f[0] == "fecha":
            return _horas_franja(f[1], f[2], f[3], a, b)
        return _dias_solapados(f[1], f[2], a, b) * 24.0

    def _es_uso(estado: str) -> bool:
        return estado in _ESTADOS_OCUPACION

    # --- demanda y uso por periodo ---
    dem_actual = [(r, t, e) for r, t, e in filas if _cruza(t, r.id, d0, d1)]
    dem_previa = [(r, t, e) for r, t, e in filas if _cruza(t, r.id, d0p, d1p)]
    uso_actual = [(r, t, e) for r, t, e in dem_actual if _es_uso(e)]
    uso_previo = [(r, t, e) for r, t, e in dem_previa if _es_uso(e)]
    horas_actual = round(sum(_horas(t, r.id, d0, d1) for r, t, _ in uso_actual), 2)
    horas_previa = round(sum(_horas(t, r.id, d0p, d1p) for r, t, _ in uso_previo), 2)
    solicitadas = sum(1 for _, _, e in dem_actual if e == "SOLICITADA")

    unidades_filas = repo.unidades(db, unidades)
    versiones_por_unidad: dict[int, list] = {}
    for u in unidades_filas:
        versiones_por_unidad[u.id_unidad] = repo.historico_horario(db, u.id_unidad)

    def _ocupacion_total(pares, a: date, b: date) -> float | None:
        total_uso = sum(_horas(t, r.id, a, b) for r, t, _ in pares)
        disps = [_horas_atencion(db, u.id_unidad, a, b) for u in unidades_filas]
        validas = [d for d in disps if d is not None]
        if not validas:
            return None
        return _porcentaje(total_uso, sum(validas))

    # --- por_estado (seis claves siempre) ---
    por_estado = {k: 0 for k in _ESTADOS_SOLICITUD}
    for _, _, e in dem_actual:
        por_estado[e.lower()] = por_estado.get(e.lower(), 0) + 1

    # --- por_fecha (franja; la salida en campus/externo) ---
    por_dia: dict[date, int] = {}
    for r, t, _ in dem_actual:
        f = _franja(r.id, t)
        if f is None:
            continue
        fecha = f[1]
        if d0 <= fecha <= d1:
            por_dia[fecha] = por_dia.get(fecha, 0) + 1
    por_fecha = [{"fecha": f.isoformat(), "reservas": por_dia[f]} for f in sorted(por_dia)]

    # --- por_laboratorio ---
    por_lab = []
    for u in unidades_filas:
        dem_u = [(r, t, e) for r, t, e in dem_actual if r.id_unidad == u.id_unidad]
        uso_u = [(r, t, e) for r, t, e in uso_actual if r.id_unidad == u.id_unidad]
        h_u = round(sum(_horas(t, r.id, d0, d1) for r, t, _ in uso_u), 2)
        por_lab.append({
            "id_unidad": u.id_unidad, "nombre": u.nombre,
            "reservas": len(dem_u), "horas_reservadas": h_u,
            "porcentaje_ocupacion": _porcentaje(h_u, _horas_atencion(db, u.id_unidad, d0, d1)),
        })
    por_lab.sort(key=lambda d: d["id_unidad"])

    # --- recursos más reservados: por asignación (una reserva con N suma N) ---
    from collections import Counter as _Counter
    conteo: _Counter[int] = _Counter()
    for r, t, _ in uso_actual:
        for a in asign.get(r.id, []):
            conteo[a.recurso_id] += 1
    top = sorted(conteo.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    mas_reservados = [
        {"recurso_id": rid, "nombre": repo.nombre_recurso(db, rid), "reservas": n}
        for rid, n in top
    ]

    # --- mapa de calor: cantidad por día×hora, grid 7–19, dentro del horario ---
    calor: _Counter[tuple[int, int]] = _Counter()
    for r, t, _ in uso_actual:
        if t not in ("ESPACIO", "RECURSO_INTERNO"):
            continue
        f = _franja(r.id, t)
        if f is None or f[0] != "fecha":
            continue
        _, fecha, h0, h1 = f
        if not (d0 <= fecha <= d1):
            continue
        versiones = versiones_por_unidad.get(r.id_unidad, [])
        version = next(
            (v for v in versiones
             if v.vigente_desde.date() <= fecha and (v.vigente_hasta is None or fecha < v.vigente_hasta.date())),
            None,
        )
        if version is None:
            continue
        if (fecha.weekday() + 1) % 7 not in (version.dias_atencion or []):
            continue
        ap = version.hora_apertura.hour * 60 + version.hora_apertura.minute
        ci = version.hora_cierre.hour * 60 + version.hora_cierre.minute
        dia = (fecha.weekday() + 1) % 7
        inicio = max(7, h0.hour)
        fin = min(20, _ceil(h1.hour + h1.minute / 60))
        for h in range(inicio, fin):
            if ap <= h * 60 < ci:
                calor[(dia, h)] += 1
    dia_hora = [
        {"dia": dia, "hora": hora, "cantidad": calor[(dia, hora)]}
        for dia in range(7) for hora in range(7, 20) if calor[(dia, hora)]
    ]

    return {
        "resumen": {
            "desde": d0.isoformat(), "hasta": d1.isoformat(),
            "desde_previo": d0p.isoformat(), "hasta_previo": d1p.isoformat(),
            "filtros": {k: v for k, v in filtros.items() if v is not None},
        },
        "indicadores": {
            "reservas": {"actual": len(dem_actual), "previo": len(dem_previa)},
            "solicitadas": solicitadas,
            "horas_reservadas": {"actual": horas_actual, "previo": horas_previa},
            "porcentaje_ocupacion": {
                "actual": _ocupacion_total(uso_actual, d0, d1),
                "previo": _ocupacion_total(uso_previo, d0p, d1p),
            },
        },
        "por_estado": por_estado,
        "por_fecha": por_fecha,
        "por_laboratorio": por_lab,
        "recursos_mas_reservados": mas_reservados,
        "ocupacion_dia_hora": dia_hora,
    }
